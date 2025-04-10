use pyo3::prelude::*;
use pyo3::types::PyList;
use pyo3::types::IntoPyDict;

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


#[pyfunction]
fn get_representation_set(full_log_path: &str) -> PyResult<PyObject> {
    // this loads the whole file in memory - don't do this on your old laptop ;)
    println!("\tloading logfile into memory");
    let bytes = fs::read(full_log_path).unwrap();
    
    let frames = parse_frames_from_bytes(&bytes);

    //println!("\tframes length: {}", frames.len());

    // TODO move this to a reader class
    let mut unique_fields = HashSet::new();
    for frame in frames.iter() {
        for field_name in frame.get_representation_names() {
            unique_fields.insert(field_name);
        }
    }
    //println!("\tUnique field names: {:?}", unique_fields);

    // Convert HashSet into a Python list
    Python::with_gil(|py| {
        let py_list = PyList::new(py, unique_fields.into_iter().collect::<Vec<_>>());
        Ok(py_list.into())
    })
}

#[pyfunction]
fn get_num_representation(full_log_path: &str) -> PyResult<PyObject> {
    // this loads the whole file in memory - don't do this on your old laptop ;)
    println!("\tloading logfile into memory");
    let bytes = fs::read(full_log_path).unwrap();

    let frames = parse_frames_from_bytes(&bytes);

    let mut field_counts = HashMap::new();
    for frame in frames {
        for (field_name, my_tuple) in &frame.fields {
            // ignore empty representations here
            if my_tuple.1 > 0 {
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

/// A Python module implemented in Rust.
#[pymodule]
fn log_crawler(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_representation_set, m)?)?;
    m.add_function(wrap_pyfunction!(get_num_representation, m)?)?;
    
    Ok(())
}