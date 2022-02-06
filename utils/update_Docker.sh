conda env export | sed 's/name: .*/name: base/'  | sed 's/prefix: .*//' > ../environment.yml
docker login ghcr.io
if [ $? -eq 1 ]
then
   echo "Please registry your self to ghcr.io"
   echo "Example : "
   echo "export CR_PAT=YOUR_TOKEN"
   echo "echo \$YOURTOKEN | docker login ghcr.io -u USERNAME --password-stdin"
fi
docker build -t ghcr.io/symmehub/positron/positron:latest ..
docker push ghcr.io/symmehub/positron/positron:latest
