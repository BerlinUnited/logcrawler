"""
    holds or generates the list of events that should be added to postgres/minio/labelstudio.
    everything inside those event folders need to be in proper structure
"""
# TODO if in k8s I should read this from a configmap, else from a local file

event_list = [
    "2019-05-01_GO19", 
    "2019-03-28_Aspen",
    "2019-06-16_Workshop",
    "2019-07-02_RC19",
    "2019-07-02_RC19-prepare",
    "2019-11-21_Koeln",
    "2021-05-06_GORE21"
]