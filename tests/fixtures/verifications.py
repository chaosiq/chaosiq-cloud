# -*- coding: utf-8 -*-

ExperimentWithoutExtensionBlock = {
    "version": "1.0.0",
    "title": "Verify something important to me!",
    "description": "Verifies an SLO under some conditions",
    "contributions": {
        "availability": "high",
        "reliability": "high",
        "safety": "none",
        "security": "none",
        "performability": "medium"
    },
    "steady-state-hypothesis": {
        "title": "Application is normal",
        "probes": [
            {
                "type": "probe",
                "name": "application-must-respond-normally",
                "tolerance": 200,
                "provider": {
                    "type": "http",
                    "url": "http://blah.com",
                    "timeout": 3
                }
            }
        ]
    },
    "method": [
        {
            "type": "probe",
            "name": "application-must-respond-normally",
            "tolerance": 200,
            "provider": {
                "type": "http",
                "url": "http://blah.com",
                "timeout": 3
            }
        }
    ],
    "rollbacks": []
}


ExperimentWithoutChaosIQExtensionBlock = {
    "version": "1.0.0",
    "title": "Verify something important to me!",
    "description": "Verifies an SLO under some conditions",
    "contributions": {
        "availability": "high",
        "reliability": "high",
        "safety": "none",
        "security": "none",
        "performability": "medium"
    },
    "extensions": [],
    "steady-state-hypothesis": {
        "title": "Application is normal",
        "probes": [
            {
                "type": "probe",
                "name": "application-must-respond-normally",
                "tolerance": 200,
                "provider": {
                    "type": "http",
                    "url": "http://blah.com",
                    "timeout": 3
                }
            }
        ]
    },
    "method": [
        {
            "type": "probe",
            "name": "application-must-respond-normally",
            "tolerance": 200,
            "provider": {
                "type": "http",
                "url": "http://blah.com",
                "timeout": 3
            }
        }
    ],
    "rollbacks": []
}


ExperimentWithoutChaosIQVerificationBlock = {
    "version": "1.0.0",
    "title": "Verify something important to me!",
    "description": "Verifies an SLO under some conditions",
    "contributions": {
        "availability": "high",
        "reliability": "high",
        "safety": "none",
        "security": "none",
        "performability": "medium"
    },
    "extensions": [
        {
            "name": "chaosiq"
        }
    ],
    "steady-state-hypothesis": {
        "title": "Application is normal",
        "probes": [
            {
                "type": "probe",
                "name": "application-must-respond-normally",
                "tolerance": 200,
                "provider": {
                    "type": "http",
                    "url": "http://blah.com",
                    "timeout": 3
                }
            }
        ]
    },
    "method": [
        {
            "type": "probe",
            "name": "application-must-respond-normally",
            "tolerance": 200,
            "provider": {
                "type": "http",
                "url": "http://blah.com",
                "timeout": 3
            }
        }
    ],
    "rollbacks": []
}


ExperimentWithoutVerificationId = {
    "version": "1.0.0",
    "title": "Verify something important to me!",
    "description": "Verifies an SLO under some conditions",
    "contributions": {
        "availability": "high",
        "reliability": "high",
        "safety": "none",
        "security": "none",
        "performability": "medium"
    },
    "extensions": [
        {
            "name": "chaosiq",
            "verification": {}
        }
    ],
    "steady-state-hypothesis": {
        "title": "Application is normal",
        "probes": [
            {
                "type": "probe",
                "name": "application-must-respond-normally",
                "tolerance": 200,
                "provider": {
                    "type": "http",
                    "url": "http://blah.com",
                    "timeout": 3
                }
            }
        ]
    },
    "method": [
        {
            "type": "probe",
            "name": "application-must-respond-normally",
            "tolerance": 200,
            "provider": {
                "type": "http",
                "url": "http://blah.com",
                "timeout": 3
            }
        }
    ],
    "rollbacks": []
}

ExperimentWithoutMeasurementFrequency = {
    "version": "1.0.0",
    "title": "Verify something important to me!",
    "description": "Verifies an SLO under some conditions",
    "contributions": {
        "availability": "high",
        "reliability": "high",
        "safety": "none",
        "security": "none",
        "performability": "medium"
    },
    "extensions": [
        {
            "name": "chaosiq",
            "verification": {
                "id": "SOME_GUID"
            }
        }
    ],
    "steady-state-hypothesis": {
        "title": "Application is normal",
        "probes": [
            {
                "type": "probe",
                "name": "application-must-respond-normally",
                "tolerance": 200,
                "provider": {
                    "type": "http",
                    "url": "http://blah.com",
                    "timeout": 3
                }
            }
        ]
    },
    "method": [
        {
            "type": "probe",
            "name": "application-must-respond-normally",
            "tolerance": 200,
            "provider": {
                "type": "http",
                "url": "http://blah.com",
                "timeout": 3
            }
        }
    ],
    "rollbacks": []
}


ExperimentWithoutConditionsDuration = {
    "version": "1.0.0",
    "title": "Verify something important to me!",
    "description": "Verifies an SLO under some conditions",
    "contributions": {
        "availability": "high",
        "reliability": "high",
        "safety": "none",
        "security": "none",
        "performability": "medium"
    },
    "extensions": [
        {
            "name": "chaosiq",
            "verification": {
                    "id": "SOME_GUID",
                    "frequency-of-measurement": {
                        "days": 0,
                        "hours": 0,
                        "minutes": 1,
                        "seconds": 0
                    }
            }
        }
    ],
    "steady-state-hypothesis": {
        "title": "Application is normal",
        "probes": [
            {
                "type": "probe",
                "name": "application-must-respond-normally",
                "tolerance": 200,
                "provider": {
                    "type": "http",
                    "url": "http://blah.com",
                    "timeout": 3
                }
            }
        ]
    },
    "method": [
        {
            "type": "probe",
            "name": "application-must-respond-normally",
            "tolerance": 200,
            "provider": {
                "type": "http",
                "url": "http://blah.com",
                "timeout": 3
            }
        }
    ],
    "rollbacks": []
}


ExperimentWithCompleteVerification = {
    "version": "1.0.0",
    "title": "Verify something important to me!",
    "description": "Verifies an SLO under some conditions",
    "contributions": {
        "availability": "high",
        "reliability": "high",
        "safety": "none",
        "security": "none",
        "performability": "medium"
    },
    "extensions": [
        {
            "name": "chaosiq",
            "verification": {
                "id": "SOME_GUID",
                "warm-up-duration": {
                    "days": 0,
                    "hours": 0,
                    "minutes": 1,
                    "seconds": 0
                },
                "frequency-of-measurement": {
                    "days": 0,
                    "hours": 0,
                    "minutes": 1,
                    "seconds": 0
                },
                "duration-of-conditions": {
                    "days": 0,
                    "hours": 0,
                    "minutes": 30,
                    "seconds": 0
                },
                "cool-down-duration": {
                    "days": 0,
                    "hours": 0,
                    "minutes": 1,
                    "seconds": 0
                }
            }
        }
    ],
    "steady-state-hypothesis": {
        "title": "Application is normal",
        "probes": [
            {
                "type": "probe",
                "name": "application-must-respond-normally",
                "tolerance": 200,
                "provider": {
                    "type": "http",
                    "url": "http://blah.com",
                    "timeout": 3
                }
            }
        ]
    },
    "method": [
        {
            "type": "probe",
            "name": "application-must-respond-normally",
            "tolerance": 200,
            "provider": {
                "type": "http",
                "url": "http://blah.com",
                "timeout": 3
            }
        }
    ],
    "rollbacks": []
}
