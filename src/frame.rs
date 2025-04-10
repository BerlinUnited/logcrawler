/*

*/
use std::collections::HashMap;
use std::fmt;

pub struct Frame{
    pub frame_number: u32,
    pub size: u32,
    pub start: u32,
    pub fields: HashMap<String, (u32, u32)>
}

impl Frame{
    pub fn new(start: u32, frame_number: u32) -> Self{
        Self {
            frame_number,
            size: 0,
            start,
            fields: HashMap::new()
        }
    }

    pub fn add_field_position(&mut self, name: &str, position: u32, size: u32) {
        self.fields.insert(name.to_string(), (position, size));
        // size of framenumber + size of string + size of payload size + payload
        self.size += 4 + (name.len() as u32 + 1) * std::mem::size_of::<u8>() as u32 + 4 + size;
    }

    pub fn get_representation_names(&self)-> Vec<&str>{
        self.fields.keys().map(|s| s.as_str()).collect()
    }
}

// Implement Display for pretty printing
impl fmt::Display for Frame {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        writeln!(f, "Frame {}:", self.frame_number)?;
        for (name, &(position, size)) in &self.fields {
            writeln!(f, "  {}: position = {}, size = {}", name, position, size)?;
        }
        Ok(())
    }
}

/*
fn main(){
    let mut a = Frame::new(0, 1);
    a.add_field_position("repr1", 0, 123);
    a.add_field_position("repr2", 30, 40);
    println!("Hello from frame {}", a.frame_number);
    println!("Hello from frame {:?}", a.get_names());
}
*/