# Image setup
source .env

# Conda setups 
BUILD_ARGS+=("--build-arg" "CONDA_DIR="$CONDA_DIR"")
BUILD_ARGS+=("--build-arg" "CONDA_ENV_NAME="$CONDA_ENV_NAME"")

# Get hardward compute capability
COMPUTE_CAPABILITY=$(nvidia-container-cli info | grep Architecture | grep -oe '\([0-9.]*\)')
BUILD_ARGS+=("--build-arg" "COMPUTE_CAPABILITY=$COMPUTE_CAPABILITY")

echo "${BUILD_ARGS[@]}"

docker build -f ./Dockerfile -t $BASE_NAME "${BUILD_ARGS[@]}" .
