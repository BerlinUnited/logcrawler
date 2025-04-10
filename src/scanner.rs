use std::error::Error;
use std::fmt;
use std::collections::HashMap;


#[derive(Debug)]
pub struct EofError;

impl fmt::Display for EofError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "Unexpected end of file")
    }
}

impl Error for EofError {}

pub fn read_long(bytes: &[u8], cursor: &mut usize) -> Result<i32, EofError> {
    let byte_slice = read_bytes(bytes, cursor, 4)?;
    Ok(i32::from_le_bytes(byte_slice.try_into().unwrap()))
}

pub fn read_bytes<'a>(bytes: &'a [u8], cursor: &'a mut usize, n: usize) -> Result<&'a[u8], EofError> {
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

pub fn read_string(bytes: &[u8], cursor: &mut usize) -> Result<String, EofError> {
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