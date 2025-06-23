use pyo3::prelude::*;
use std::fs;
use std::collections::HashSet;
use std::collections::HashMap;
use pyo3::types::PyList;
use pyo3::types::IntoPyDict;
use pyo3::types::PyDict;
use pyo3::types::PyTuple;

//use serde::Serialize;
use kdam::tqdm;

mod crawler {
    // Include all files as if they were part of this module
    include!("reader.rs");
    include!("scanner.rs");
    include!("frame.rs");
}

pub use crawler::parse_frames_from_bytes;

#[pyclass]  // Expose the struct to Python
struct LogCrawler {
    #[pyo3(get, set)]  // Optional: Allow Python to access/modify field
    log_path: String,
    bytes: Vec<u8>,
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

    fn get_representation_metadata(&mut self, representation: String) -> PyResult<PyObject> {
        let frames = parse_frames_from_bytes(&self.bytes);

        let mut data = HashMap::new();
        for frame in frames{
            for (field_name, my_tuple) in &frame.fields {
                // ignore empty representations here
                if my_tuple.1 > 0  && field_name == &representation{
                    let start: usize = my_tuple.0 as usize;
                    let size: usize = my_tuple.1 as usize;

                    data.insert(frame.frame_number, (start, size));
                }
            }
        }
        // FIXME: return a dict frame_number: data
        Python::with_gil(|py| {
            let py_dict = PyDict::new(py);
            for (frame_number, (start, size)) in data {
                // Create a Python tuple for the start and size values
                let py_tuple = PyTuple::new(py, &[start.into_py(py), size.into_py(py)]);
                py_dict.set_item(frame_number, py_tuple)?;
            }
            Ok(py_dict.into())
        })
    }
}


/// A Python module implemented in Rust.
#[pymodule]
fn log_crawler(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<LogCrawler>()?;
    Ok(())
}

