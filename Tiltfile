allow_k8s_contexts('berlinunited')

default_registry('ttl.sh/iamacooluser-asdasdasdassdqadqweddher')

docker_build('example-python-image', '.')
k8s_yaml('kubernetes.yaml')
k8s_resource('log-crawler2', port_forwards=8000)