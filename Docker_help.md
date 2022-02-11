# Update docker image

If you need to update the **environment.yml**. You can also create an associate docker image and use it for the CI run. 

1. Update **environment.yml** with yours modules.
   - ***Warning***: Don't forget to include *Jupyter-book* module

            conda install -c conda-forge jupyter-book

    - Export a conda environment:
        
            conda activate "your_env_name"
            conda env export | sed 's/name: .*/name: base/'  | sed 's/prefix: .*//' > environment.yml

    
      **Note**: We make sure that environment name is ***"base"***

2. Build your docker image.

        docker build -t <image_name>:<tag_name> <path_to_Dockerfile> <path_to_your_dockerfile>
   
    - Example with my DockerHub account. Current directory is **positron/**.

            docker build -t celmo/jupyter-book:latest .

    - Example with **GitHub Rgistry (Packages)**:

            docker build -t ghcr.io/symmehub/positron/positron:latest .
            
3. Push your docker image
   1. On ***DockerHub***:
      1. Having a DockerHub account see [here](https://docs.docker.com/docker-hub/)
      2. Run the following command:
           
             docker push <image_name>:<tag_name>

         Example:
                
             docker push celmo/jupyter-book:latest 
   2. On ***GitHub*** registry (also known as ***GitHub Packages***)
      1. Log to Github registry with docker:

          - Create personal access token for the command line see [here](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line)
   
          - Save your PAT as an environment variable.

                export CR_PAT=YOUR_TOKEN

          - Using the CLI for your container type, sign in to the Container registry service at ghcr.io.

                echo $CR_PAT | docker login ghcr.io -u USERNAME --password-stdin

      2. Push container to GitHub registry:
    
             docker push ghcr.io/symmehub/positron/positron:latest

      3. Optional inspect:

             docker inspect ghcr.io/symmehub/positron/positron:latest
