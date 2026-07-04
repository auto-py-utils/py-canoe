*** Settings ***
Library    py_canoe.canoe_robot_lib.CanoeRobotLib
Library    Collections

*** Variables ***
${TEST_DIR}    ${CURDIR}
${DEMO_CFG_DIR}    ${TEST_DIR}${/}..${/}demo_cfg
${DEMO_CFG_DEV}    ${DEMO_CFG_DIR}${/}demo_dev.cfg
${DEMO_CFG_DIAG}    ${DEMO_CFG_DIR}${/}demo_diag.cfg
${DEMO_CFG_TEST_SETUP}    ${DEMO_CFG_DIR}${/}demo_test_setup.cfg
${DEMO_CFG_GEN_DB_SETUP}    ${DEMO_CFG_DIR}${/}demo_conf_gen_db_setup.cfg
${DEMO_CFG_ONLINE_SETUP}    ${DEMO_CFG_DIR}${/}demo_online_setup.cfg
${DEMO_LOG_BLF}    ${DEMO_CFG_DIR}${/}Logs${/}demo_log.blf
${DEMO_ONLINE_SETUP_LOG_BLF}    ${DEMO_CFG_DIR}${/}Logs${/}demo_online_setup_log.blf
${XCP_DBC}    ${DEMO_CFG_DIR}${/}DBs${/}sample_databases${/}XCP.dbc

*** Test Cases ***
Opening Different Cfgs Sequentially
    ${status}=    Canoe Open    canoe_cfg=${DEMO_CFG_DEV}    visible=True    auto_save=False    prompt_user=False
    Should Be True    ${status}
    ${status}=    Canoe Start Measurement
    Should Be True    ${status}
    ${status}=    Canoe Stop Measurement
    Should Be True    ${status}
    Sleep    1s
    ${status}=    Canoe Open    canoe_cfg=${DEMO_CFG_DIAG}    visible=True    auto_save=False    prompt_user=False
    Should Be True    ${status}
    ${status}=    Canoe Start Measurement
    Should Be True    ${status}
    ${status}=    Canoe Stop Measurement
    Should Be True    ${status}
    Sleep    1s
    ${status}=    Canoe Open    canoe_cfg=${DEMO_CFG_TEST_SETUP}    visible=True    auto_save=False    prompt_user=False
    Should Be True    ${status}
    ${status}=    Canoe Start Measurement
    Should Be True    ${status}
    ${status}=    Canoe Stop Measurement
    Should Be True    ${status}
    Sleep    1s


Measurement Start Stop Restart Methods
    ${status}=    Canoe Open    canoe_cfg=${DEMO_CFG_DEV}    visible=True    auto_save=False    prompt_user=False
    Should Be True    ${status}
    ${status}=    Canoe Start Measurement
    Should Be True    ${status}
    ${status}=    Canoe Stop Measurement
    Should Be True    ${status}
    ${status}=    Canoe Start Measurement
    Should Be True    ${status}
    ${status}=    Canoe Reset Measurement
    Should Be True    ${status}
    ${status}=    Canoe Get Measurement Running Status
    Should Be True    ${status}
    ${status}=    Canoe Stop Ex Measurement
    Should Be True    ${status}
    ${status}=    Canoe Get Measurement Running Status
    Should Not Be True    ${status}
    ${status}=    Canoe Quit
    Should Be True    ${status}
