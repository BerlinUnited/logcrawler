"""
    holds or generates the list of events that should be added to postgres/minio/labelstudio.
    everything inside those event folders need to be in proper structure
"""

# TODO if in k8s I should read this from a configmap, else from a local file

event_list = [
    "2019-03-03-RoDeo",
    "2019-03-28_Aspen",
    "2019-05-01_GO19",
    "2019-06-15_LNDW19",
    "2019-06-16_Workshop",
    "2019-07-02_RC19",
    "2019-07-02_RC19-prepare",
    "2019-11-21_Koeln",
    "2021-05-06_GORE21",
    "2022-06-23_futurework22",
    "2023-04-29-GORE",
    "2023-08-cccamp",
    "2023-12-03-RoHOW",
    "2023-10-18-semesterproject-intro-R0101",
]

experiment_list = [
    "2019-05-01_GO19/Experiments/ball_detection/earpiece.log",
    "2019-05-01_GO19/Experiments/ball_detection/jerseys_back.log",
    "2019-05-01_GO19/Experiments/ball_detection/jerseys_front.log",
    "2019-05-01_GO19/Experiments/ball_detection/moving_ball_1.log",
    "2019-05-01_GO19/Experiments/ball_detection/moving_ball_2.log",
    "2019-05-01_GO19/Experiments/ball_detection/robot_moving_seeing_ball.log",
    "2019-05-01_GO19/Experiments/ball_detection/robot_moving_seeing_v6.log",
    "2019-05-01_GO19/Experiments/ball_detection/seeing_v6_robot.log",
    "2019-05-01_GO19/Experiments/field_detection/behind_goal.log",
    "2019-05-01_GO19/Experiments/field_detection/go16-field-1.log",
    "2019-05-01_GO19/Experiments/field_detection/go16-field-2.log",
    "2019-05-01_GO19/Experiments/field_detection/go19_localize1.log",
    "2019-05-01_GO19/Experiments/field_detection/go19_localize2.log",
    "2019-05-01_GO19/Experiments/field_detection/go19_ready_play.log",
    "2019-05-01_GO19/Experiments/field_detection/go19_set_play.log",
    "2019-05-01_GO19/Experiments/field_detection/goalie_box.log",
    "2019-05-01_GO19/Experiments/field_detection/goalie_lookaround.log",
    "2019-05-01_GO19/Experiments/field_detection/integral_too_small.log",
    "2019-05-01_GO19/Experiments/field_detection/sideline.log",
    "2019-05-01_GO19/Experiments/go19_us_test/us_blue_jersey.log",
    "2019-05-01_GO19/Experiments/go19_us_test/us_white_jersey.log",
    "2019-05-01_GO19/Experiments/go19_us_test/us_without_jersey.log",
    "2019-05-01_GO19/Experiments/line_detection/go19_localize1.log",
    "2019-05-01_GO19/Experiments/line_detection/go19_localize2.log",
    "2019-05-01_GO19/Experiments/line_detection/go19_ready_play.log",
    "2019-05-01_GO19/Experiments/line_detection/go19_set_play.log",
    "2019-05-01_GO19/Experiments/line_detection/goalie_box.log",
    "2019-05-01_GO19/Experiments/line_detection/goalie_lookaround.log",
    "2019-07-02_RC19/Experiments/vision/INDOOR/GOALY_SET.log",
    "2019-07-02_RC19/Experiments/vision/INDOOR/PLAY.log",
    "2019-07-02_RC19/Experiments/vision/INDOOR/PLAY_FROM_CIRCLE_GOAL.log",
    "2019-07-02_RC19/Experiments/vision/INDOOR/PLAY2.log",
    "2019-07-02_RC19/Experiments/vision/INDOOR/PLAY3_TILL_FALL.log",
    "2019-07-02_RC19/Experiments/vision/INDOOR/RANDOM_SET_BY_CIRCLE.log",
    "2019-07-02_RC19/Experiments/vision/INDOOR/RANDOM_SET_LEFT.log",
    "2019-07-02_RC19/Experiments/vision/INDOOR/READY_OFFSET_LOCA.log",
    "2019-07-02_RC19/Experiments/vision/INDOOR/READY_OFFSET_LOCA_2.log",
    "2019-07-02_RC19/Experiments/vision/INDOOR/READY_WEIRD_LOCA.log",
    "2019-07-02_RC19/Experiments/vision/INDOOR/SET_CIRCLE_RANDOM_GO.log",
    "2019-07-02_RC19/Experiments/vision/INDOOR/STRIKER_FROM_GOAL.log",
    "2019-07-02_RC19/Experiments/vision/OUTDOOR/1.log",
    "2019-07-02_RC19/Experiments/vision/OUTDOOR/2.log",
    "2019-07-02_RC19/Experiments/vision/OUTDOOR/3.log",
    "2019-07-02_RC19/Experiments/vision/OUTDOOR/4.log",
    "2019-07-02_RC19/Experiments/vision/OUTDOOR/5.log",
    "2019-07-02_RC19/Experiments/vision/OUTDOOR/6.log",
    "2019-07-02_RC19/Experiments/vision/OUTDOOR/stand.log",
    "2019-07-02_RC19/Experiments/vision/double_field_lines.log",
    "2019-07-02_RC19/Experiments/test_goalie/4_94_Nao0338_090917-2255/game.log",
    "2019-07-02_RC19/Experiments/path2018_usoa_futureball/1_94_Nao0338_090918-1315/game.log",
    "2019-07-02_RC19/Experiments/3_94_Nao0338_090918-2203_scangridedgeldetector_uniform_lengths/game.log",
    "2020-03-08-RoDeo-Experiments/rodeo20_test1.log",
    # "2020-03-08-RoDeo-Experiments/0_16_nao_lola_200308-1343/cognition.log", # TODO check this manually
    # "2023-07-04_RC23/Experiments/3_16_Nao0017_230704-0846/combined.log", # FIXME manually combine this again so that the image order is correct
    # "2023-07-04_RC23/Experiments/cognition_fall_down_tests_markus.log", FIXME seems to not have meta information
    "2023-07-04_RC23/Experiments/cognition1_ball.log",
    "2023-07-04_RC23/Experiments/cognition2_ball.log",
    "2023-07-04_RC23/Experiments/cognition3_ball.log",
    "2023-07-04_RC23/Experiments/cognition4_ball.log",
    "2023-07-04_RC23/Experiments/cognition5_ball.log",
    "2024-04-17_GO24/Experiments/first.log",  # TODO: Feld B
    "2024-04-17_GO24/Experiments/second.log",  # TODO: Feld B
    "2024-04-17_GO24/Experiments/ball_in_the_wall_1.log",  # TODO: Feld B
    "2024-04-17_GO24/Experiments/ball_in_the_wall_2.log",  # TODO: Feld B
    "2024-04-17_GO24/Experiments/ball_in_the_wall_3.log",  # TODO: Feld B
    "2024-04-17_GO24/Experiments/felda_cognition1.log",
    "2024-04-17_GO24/Experiments/felda_cognition2.log",
    "2024-04-17_GO24/Experiments/felda_cognition3.log",
    "2024-04-17_GO24/Experiments/feldb_cognition1.log",
    "2024-04-17_GO24/Experiments/feldb_cognition2.log",
    "2024-04-17_GO24/Experiments/feldb_cognition3.log",
]
