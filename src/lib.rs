use pyo3::prelude::*;
use pyo3::types::PyList;
use pyo3::types::IntoPyDict;
use pyo3::types::PyDict;
use serde_pyobject::to_pyobject;
use serde::Serialize;

//use serde::Serialize;
use kdam::tqdm;
pub mod naothmessages {
    include!(concat!(env!("OUT_DIR"), "/naothmessages.rs"));
}
mod crawler {
    // Include all files as if they were part of this module
    include!("reader.rs");
    include!("scanner.rs");
    include!("frame.rs");
}

pub use crawler::parse_frames_from_bytes;
use std::fs;
use std::collections::HashSet;
use std::collections::HashMap;

use naothmessages::*; // Import all types from naothmessages
use prost::Message;

#[pyclass]  // Expose the struct to Python
struct LogCrawler {
    #[pyo3(get, set)]  // Optional: Allow Python to access/modify field
    log_path: String,
    bytes: Vec<u8>,
}

fn parse_representation2<T: Message + Default>(data: &[u8]) -> Result<T, prost::DecodeError> {
    T::decode(data)
}
/*
fn parse_representation(data: &[u8]) -> Result<SensorJointData, prost::DecodeError> {
    SensorJointData::decode(data)
}
*/

fn message_to_json<T: Message + serde::Serialize>(message: &T) -> serde_json::Result<String> {
    Python::with_gil(|py| {
        let obj: Bound<PyAny> = to_pyobject(py, &message).unwrap();
        println!("{:?}", obj);
    });
    
    serde_json::to_string(message)
}


#[pymethods]
impl LogCrawler {
    #[new]  // Constructor for Python
    fn new(log_path: String) -> PyResult<Self> {
        let bytes = fs::read(&log_path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to read file: {}", e)))?;
        
        Ok(LogCrawler {
            log_path,
            bytes,
        })
    }

    fn get_representation_set(&mut self) -> PyResult<PyObject> {
        let frames = parse_frames_from_bytes(&self.bytes);

        // TODO move this to a reader class
        let mut unique_fields = HashSet::new();
        for frame in frames.iter() {
            for field_name in frame.get_representation_names() {
                unique_fields.insert(field_name);
            }
        }

        // Convert HashSet into a Python list
        Python::with_gil(|py| {
            let py_list = PyList::new(py, unique_fields.into_iter().collect::<Vec<_>>());
            Ok(py_list.into())
        })
    }

    fn get_num_representation(&mut self) -> PyResult<PyObject> {
        let frames = parse_frames_from_bytes(&self.bytes);
    
        let mut field_counts = HashMap::new();
        for frame in frames {
            for (field_name, my_tuple) in &frame.fields {
                // ignore empty representations here
                if my_tuple.1 > 0 {
                    // TODO try to parse the representation here

                    *field_counts.entry(field_name.clone()).or_insert(0) += 1;
                }
            }
        }
    
        // Convert HashMap into a Python dictionary
        Python::with_gil(|py| {
            let py_dict = field_counts.into_py_dict(py);
            Ok(py_dict.into())
        })
    }

    fn get_representation(&mut self) -> PyResult<PyObject> {
        let frames = parse_frames_from_bytes(&self.bytes);
        let mut jpeg_data = Vec::new();
    
        for frame in tqdm!(frames.iter()) {
            for (field_name, my_tuple) in &frame.fields {
                // ignore empty representations here
                if my_tuple.1 > 0  && field_name == "ImageJPEGTop"{
                    //println!("ImageJPEGTop");
                    let start: usize = my_tuple.0 as usize;
                    let size: usize = my_tuple.1 as usize;
    
                    // Read the byte slice from bytes
                    let slice = &self.bytes[start..start+size];
                    jpeg_data.push(slice);
                    /*
                    if let Ok(image) = Image::decode(slice) {
                        jpeg_data.push(image);
                    }*/
                }
            }
        };
        //println!("Parsed ImageJPEGTop: {:?}", jpeg_data[0]);
    
        Python::with_gil(|py| {
            let py_list = PyList::new(py, jpeg_data);
            Ok(py_list.into())
        })
    }

    fn get_unparsed_representation_list(&mut self, representation: String) -> PyResult<PyObject> {
        let frames = parse_frames_from_bytes(&self.bytes);
        //let mut data = Vec::new();
        let mut data = HashMap::new();
        for frame in frames{
            for (field_name, my_tuple) in &frame.fields {
                // ignore empty representations here
                if my_tuple.1 > 0  && field_name == &representation{
                    let start: usize = my_tuple.0 as usize;
                    let size: usize = my_tuple.1 as usize;

                    // Read the byte slice from bytes
                    let slice = &self.bytes[start..start+size];
                    //data.push(slice);
                    data.insert(frame.frame_number, slice);
                }
            }
        }
        // FIXME: return a dict frame_number: data
        Python::with_gil(|py| {
            let py_dict = data.into_py_dict(py);
            Ok(py_dict.into())
        })

    }
    
        fn get_first_representation2(&mut self, representation: String) -> PyResult<PyObject> {
            let frames = parse_frames_from_bytes(&self.bytes);

            let mut data = Vec::new();
            for (field_name, my_tuple) in &frames[0].fields {
                // ignore empty representations here
                if my_tuple.1 > 0  && field_name == &representation{
                    let start: usize = my_tuple.0 as usize;
                    let size: usize = my_tuple.1 as usize;

                    // Read the byte slice from bytes
                    let slice = &self.bytes[start..start+size];
                    
                    let repr = match parse_representation2(&slice) {
                        Ok(value) => value,
                        Err(e) => {
                            println!("Error: {}", e);
                            break;
                        }
                    };
                    println!("Error: {:?}", repr);
                    data.push(repr)
                }
            }

            Python::with_gil(|py| {
                let obj = to_pyobject(py, &data[0]).unwrap();
                Ok(obj.into())
            })

        }
}

#[pyfunction]
fn get_representation(full_log_path: &str) -> PyResult<PyObject> {
    println!("\tloading logfile into memory");
    let bytes = fs::read(full_log_path).unwrap();

    let frames = parse_frames_from_bytes(&bytes);
    let mut jpeg_data = Vec::new();

    for frame in tqdm!(frames.iter()) {
        for (field_name, my_tuple) in &frame.fields {
            // ignore empty representations here
            if my_tuple.1 > 0  && field_name == "ImageJPEGTop"{
                //println!("ImageJPEGTop");
                let start: usize = my_tuple.0 as usize;
                let size: usize = my_tuple.1 as usize;

                // Read the byte slice from bytes
                let slice = &bytes[start..start+size];
                jpeg_data.push(slice);
                /*
                if let Ok(image) = Image::decode(slice) {
                    jpeg_data.push(image);
                }*/
            }
        }
    };
    
    Python::with_gil(|py| {
        let py_list = PyList::new(py, jpeg_data);
        Ok(py_list.into())
    })
}


/// A Python module implemented in Rust.
#[pymodule]
fn log_crawler(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<LogCrawler>()?;
    m.add_function(wrap_pyfunction!(get_representation, m)?)?;
    Ok(())
}

