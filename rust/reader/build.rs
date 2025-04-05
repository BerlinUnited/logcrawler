// build.rs
use std::io::Result;
fn main() -> Result<()> {
    prost_build::compile_protos(&["protos/AudioData.proto"], &["protos/"])?;
    prost_build::compile_protos(&["protos/CommonTypes.proto"], &["protos/"])?;
    prost_build::compile_protos(&["protos/Framework-Representations.proto"], &["protos/"])?;
    prost_build::compile_protos(&["protos/Messages.proto"], &["protos/"])?;
    prost_build::compile_protos(&["protos/Representations.proto"], &["protos/"])?;
    prost_build::compile_protos(&["protos/RobotPose.proto"], &["protos/"])?;
    prost_build::compile_protos(&["protos/TeamMessage.proto"], &["protos/"])?;
    Ok(())
}