#! /bin/bash -x

# Log the start of the build process
echo "Build Started for ADAPT Framework...!"
cwd=$PWD

# Check if the first argument is centralsystem or not, and if it's the case or if the first argument is all.
if [ "$1" == "centralsystem" ] || [ "$1" == "all" ]; then
    # Log the start of building the central system
    echo "Building Central System"
    
    # Remove any existing build directory to ensure a clean build
    cd $cwd
    rm -rf build

    # Create a new build directory
    mkdir build

    # Change into the build directory
    cd build

    # Copy the necessary files for the central system into the build directory
    cp -r ../central_system .
    cp -r ../adaptutils .
    cp central_system/dockerfile .
    cp central_system/requirements.txt .

    # Build a Docker image tagged as centralsystem:0.0.1 and log the success message
    docker build -t centralsystem:0.0.1 .
    echo "Central System is built Successfully...!"
fi

# Check if the first argument is detectionengine or not, and if it's the case or if the first argument is all.
if [ "$1" == "detectionengine" ] || [ "$1" == "all" ]; then
    # Log the start of building the detection engine
    echo "Building Detection Engine"

    # Remove any existing build directory to ensure a clean build
    cd $cwd
    rm -rf build

    # Create a new build directory
    mkdir build

    # Change into the build directory
    cd build

    # Copy the necessary files for the detection engine into the build directory
    cp -r ../detection_engine .
    cp -r ../adaptutils .
    cp detection_engine/dockerfile .
    cp detection_engine/requirements.txt .

    # Build a Docker image tagged as detection_engine:0.0.1 and log the success message
    docker build -t detection_engine:0.0.1 .
    echo "Detection Engine is built Successfully...!"
fi

# Check if the first argument is propagationengine or not, and if it's the case or if the first argument is all.
if [ "$1" == "propagationengine" ] || [ "$1" == "all" ]; then
    # Log the start of building the propagation engine
    echo "Building Propagation Engine"

    # Remove any existing build directory to ensure a clean build
    cd $cwd
    rm -rf build

    # Create a new build directory
    mkdir build

    # Change into the build directory
    cd build

    # Copy the necessary files for the propagation engine into the build directory
    cp -r ../propagation_engine .
    cp -r ../adaptutils .
    cp propagation_engine/dockerfile .
    cp propagation_engine/requirements.txt .

    # Build a Docker image tagged as propagation_engine:0.0.1 and log the success message
    docker build -t propagation_engine:0.0.1 .
    echo "Propagation Engine is built Successfully...!"
fi

# Log the completion of the build process
echo "Build Completed for ADAPT Framework...!"