#! /bin/bash -x

# Stop on error
set -e

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
    cp central_system/main.py .
    cp -r central_system/ui/* .

    # Build a Docker image tagged as sms2sakthivel/adapt_central_system:latest and log the success message
    IMAGE_NAME="sms2sakthivel/adapt_central_system"
    docker build -t $IMAGE_NAME:latest .
    # docker buildx build --platform linux/amd64,linux/arm64 -t $IMAGE_NAME:latest .
    if [ "$2" == "push" ] || [ "$3" == "push" ] || [ "$4" == "push" ]; then
        # Push the image if the build succeeds
        docker push -t $IMAGE_NAME:latest .
        # docker buildx build --platform linux/amd64,linux/arm64 -t $IMAGE_NAME:latest --push .
    fi
    echo "Central System is built Successfully...!"
fi

# Check if the first argument is detectionengine or not, and if it's the case or if the first argument is all.
if [ "$1" == "detectionengine.github" ] || [ "$1" == "all" ]; then
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
    cp detection_engine/github/dockerfile .
    cp detection_engine/requirements.txt .
    cp detection_engine/github/app.py .

    # Build a Docker image tagged as sms2sakthivel/adapt_detection_engine:latest and log the success message
    IMAGE_NAME="sms2sakthivel/adapt_detection_engine_github"
    docker build -t $IMAGE_NAME:latest .
    # docker buildx build --platform linux/amd64,linux/arm64 -t $IMAGE_NAME:latest .
    if [ "$2" == "push" ] || [ "$3" == "push" ] || [ "$4" == "push" ]; then
        # docker buildx build --platform linux/amd64,linux/arm64 -t $IMAGE_NAME:latest --push .
        # Push the image if the build succeeds
        docker push "$IMAGE_NAME:latest"
    fi
    echo "Detection Engine is built Successfully...!"
fi

# Check if the first argument is detectionengine or not, and if it's the case or if the first argument is all.
if [ "$1" == "detectionengine.jira" ] || [ "$1" == "all" ]; then
    # Log the start of building the detection engine
    echo "Building Detection Engine Service"

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
    cp detection_engine/jira/dockerfile .
    cp detection_engine/requirements.txt .
    cp detection_engine/jira/app.py .
    cp detection_engine/.env .

    # Build a Docker image tagged as sms2sakthivel/adapt_detection_engine:latest and log the success message
    IMAGE_NAME="sms2sakthivel/adapt_detection_engine_jira"
    docker build -t $IMAGE_NAME:latest .
    # docker buildx build --platform linux/amd64,linux/arm64 -t $IMAGE_NAME:latest .
    if [ "$2" == "push" ] || [ "$3" == "push" ] || [ "$4" == "push" ]; then
        # docker buildx build --platform linux/amd64,linux/arm64 -t $IMAGE_NAME:latest --push .
        # Push the image if the build succeeds
        docker push "$IMAGE_NAME:latest"
    fi
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
    cp propagation_engine/app.py .
    cp propagation_engine/pullrequestmanager.2025-02-22.private-key.pem .
    chmod 400 pullrequestmanager.2025-02-22.private-key.pem

    # Build a Docker image tagged as sms2sakthivel/adapt_propagation_engine:latest and log the success message
    IMAGE_NAME="sms2sakthivel/adapt_propagation_engine"
    docker build -t $IMAGE_NAME:latest .
    # docker buildx build --platform linux/amd64,linux/arm64 -t $IMAGE_NAME:latest .
    if [ "$2" == "push" ] || [ "$3" == "push" ] || [ "$4" == "push" ]; then
        # docker buildx build --platform linux/amd64,linux/arm64 -t $IMAGE_NAME:latest --push .
        # Push the image if the build succeeds
        docker push "$IMAGE_NAME:latest"
    fi
    echo "Propagation Engine is built Successfully...!"
fi

cd $cwd
rm -rf build
# Log the completion of the build process
echo "Build Completed for ADAPT Framework...!"
