
pub fn parse_frames_from_bytes(bytes: &[u8]) -> Vec<Frame> {
    let mut frames = Vec::new();  // This will store all completed frames
    let mut current_frame: Option<Frame> = None;  // Tracks the frame we're currently building
    let mut last_frame_number = None;  // Remembers the previous frame number
    let mut cursor = 0;

    let mut payload_start;

    // go through all the bytes
    while cursor < bytes.len() {
        // parse frame number
        let frame_number = match read_long(&bytes, &mut cursor) {
            Ok(value) => value,
            Err(e) => {
                println!("Error: {}", e);
                break;
            }
        };

        let name = match read_string(&bytes, &mut cursor) {
            Ok(value) => value,
            Err(e) => {
                println!("Error: {}", e);
                break;
            }
        };
        

        let message_size = match read_long(&bytes, &mut cursor) {
            Ok(value) => value,
            Err(e) => {
                println!("Error: {}", e);
                break;
            }
        };

        payload_start = cursor;
        
        // Read and parse the protobuf message
        let message_bytes = match read_bytes(&bytes, &mut cursor, message_size as usize) {
            Ok(b) => b,
            Err(e) => {
                println!("Error reading message bytes: {}", e);
                break;
            }
        };

        // Check if we need a new frame
        if last_frame_number != Some(frame_number) {
            // If we were working on a frame, push it to the list
            if let Some(frame) = current_frame.take() {
                //println!("Hello from frame {:?}", frame.get_field_names_ref());
                frames.push(frame);
                //println!("{}", frame_number);
            }
            
            // Create a new frame
            current_frame = Some(Frame::new(cursor as u32, frame_number as u32));
            last_frame_number = Some(frame_number);
        }

        // Add field to the current frame (which is guaranteed to exist at this point)
        if let Some(ref mut frame) = current_frame {
            // TODO cursor is wrong here because we already go through message_bytes
            // second argument is the start of the payload data
            frame.add_field_position(&name, payload_start as u32, message_size as u32);
        }
    }

    // Don't forget to add the last frame to the list
    if let Some(frame) = current_frame.take() {
        // this skips the frame as soon as a representation is not fully there and only the metadata for a representation was written
        // e.g. add_field_position was called for a representation but the data is not in the log
        if frame.start + frame.size <= bytes.len() as u32 {
            frames.push(frame);
        }
    }

    frames
}