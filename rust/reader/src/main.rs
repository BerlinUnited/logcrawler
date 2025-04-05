// Include the generated protobuf code
pub mod naothmessages {
    include!(concat!(env!("OUT_DIR"), "/naothmessages.rs"));
}

mod frame;  // Declares the `frame` module
use frame::Frame;  // Imports `Frame` for use

use std::fs;
use std::error::Error;
use std::fmt;


#[derive(Debug)]
struct EofError;

impl fmt::Display for EofError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "Unexpected end of file")
    }
}

impl Error for EofError {}

fn read_long(bytes: &[u8], cursor: &mut usize) -> Result<i32, EofError> {
    let byte_slice = read_bytes(bytes, cursor, 4)?;
    Ok(i32::from_le_bytes(byte_slice.try_into().unwrap()))
}

fn read_bytes<'a>(bytes: &'a [u8], cursor: &'a mut usize, n: usize) -> Result<&'a[u8], EofError> {
    if n == 0 {
        return Ok(&[]);
    }
    
    if *cursor + n > bytes.len() {
        return Err(EofError);
    }
    
    let slice = &bytes[*cursor..*cursor + n];
    *cursor += n;
    Ok(slice)
}

fn read_string(bytes: &[u8], cursor: &mut usize) -> Result<String, EofError> {
    let mut chars = Vec::new();
    
    loop {
        if *cursor >= bytes.len() {
            return Err(EofError);
        }
        
        let c = bytes[*cursor];
        *cursor += 1;
        
        if c == b'\0' {
            break;
        }
        
        chars.push(c);
    }
    
    // Convert bytes to UTF-8 string
    String::from_utf8(chars).map_err(|_| EofError)
}



fn main() {
    let bytes = fs::read("/mnt/d/logs/2025-03-12-GO25/2025-03-15_17-15-00_BerlinUnited_vs_Hulks_half2/game_logs/7_33_Nao0022_250315-1822/combined.log").unwrap();
    let mut frames = Vec::new();  // This will store all completed frames
    let mut current_frame: Option<Frame> = None;  // Tracks the frame we're currently building
    let mut last_frame_number = None;  // Remembers the previous frame number
    let mut cursor = 0;
    // go through all the bytes
    while cursor < bytes.len() {
        // parse frame number
        let frame_number = match read_long(&bytes, &mut cursor) {
            Ok(value) => value,
            Err(e) => {
                println!("Error: {}", e);
                return;
            }
        };

        let name = match read_string(&bytes, &mut cursor) {
            Ok(value) => value,
            Err(e) => {
                println!("Error: {}", e);
                return;
            }
        };

        let message_size = match read_long(&bytes, &mut cursor) {
            Ok(value) => value,
            Err(e) => {
                println!("Error: {}", e);
                return;
            }
        };

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
            }
            
            // Create a new frame
            current_frame = Some(Frame::new(cursor as u32, frame_number as u32));
            last_frame_number = Some(frame_number);
            println!("{}", frame_number);
        }

        // Add field to the current frame (which is guaranteed to exist at this point)
        if let Some(ref mut frame) = current_frame {
            
            frame.add_field_position(&name, cursor as u32, message_size as u32);
        }

        //cursor += message_size as usize;
        
        //println!("------------------");  // Separator between frames
        //println!("Hello from frame {:?}", a.get_names());
    }

    // Don't forget to add the last frame to the list
    if let Some(frame) = current_frame.take() {
        // TODO add check here
        if frame.start + frame.size <= bytes.len() as u32 {
            frames.push(frame);
        }
    }
    println!("frames length: {}", frames.len())
    /*
    // Example usage:
    match read_bytes(&bytes, &mut cursor, 4) {
        Ok(data) => println!("Read 4 bytes: {:?}", data),
        Err(e) => println!("Error: {}", e),
    }
    */
    //for byte in bytes.iter() {
        //println!("{:b}", byte);
    //}
}