// build.rs

use std::io::Result;


fn main() -> Result<()> {
    /*
    prost_build::compile_protos(&["protos/AudioData.proto"], &["protos/"])?;
    prost_build::compile_protos(&["protos/CommonTypes.proto"], &["protos/"])?;
    prost_build::compile_protos(&["protos/Framework-Representations.proto"], &["protos/"])?;
    prost_build::compile_protos(&["protos/Messages.proto"], &["protos/"])?;
    prost_build::compile_protos(&["protos/Representations.proto"], &["protos/"])?;
    prost_build::compile_protos(&["protos/RobotPose.proto"], &["protos/"])?;
    prost_build::compile_protos(&["protos/TeamMessage.proto"], &["protos/"])?;
    */
    let mut prost_build = prost_build::Config::new();
    prost_build
        .type_attribute(
            ".",
            "#[derive(serde::Serialize,serde::Deserialize)]"
        )
        .compile_protos(
            &[
                "protos/AudioData.proto",
                "protos/CommonTypes.proto",
                "protos/Framework-Representations.proto",
                "protos/Messages.proto",
                "protos/Representations.proto",
                "protos/RobotPose.proto",
                "protos/TeamMessage.proto"
            ],
            &["protos/"],
        )
        .unwrap();


    Ok(())
}