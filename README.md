# Rapid Prototyping for Climate Control Development


## Project Overview

This project focused on developing a **Rapid Control Prototyping (RCP)** system for climate control in an electric vehicle. The objective was to integrate hardware and software components, develop a functional climate-control prototype, and test its behavior before deployment on a production electronic control unit (ECU).

## System Development

A **dSPACE MicroAutoBox II** was used as a real-time prototype controller. The system integrated climate-control sensors and actuators, including stepper motors for HVAC air-distribution and temperature flaps, and the blower.

**MATLAB/Simulink** and **Stateflow** were used for model-based software development. **LIN (Local Interconnect Network)** supported communication with relevant sensors and actuators, and **dSPACE ControlDesk** was used to monitor signals, adjust parameters, and conduct real-time experiments.

## Project Work

- Worked on hardware–software integration of climate-control components with the prototype ECU.
- Developed and configured Simulink models for control and LIN communication.
- Integrated stepper-driver functions and actuator operating modes.
- Used ControlDesk to test stepper movement, requested positions, blower operation, and communication behavior.
- Used Git and Jira to support collaborative development and issue tracking.

## Development Workflow

The prototype was developed and tested through a model-based workflow:

**MATLAB / Simulink / Stateflow** (control model development) → **dSPACE MicroAutoBox II** (real-time execution) → **LIN communication** (sensor and actuator interfaces) → **dSPACE ControlDesk** (monitoring and testing).

## Testing and Validation

Using ControlDesk, the stepper drivers and blower were tested separately to observe their response to control requests. Stepper testing included checking commanded positions and movement of the HVAC flaps. LIN communication and component behavior were monitored to support troubleshooting and system integration.

The internship report documents successful stepper-driver and blower testing; **complete sensor testing was still pending**.

## Technical Skills

| Area | Tools and Technologies |
| --- | --- |
| Model-based development | MATLAB, Simulink, Stateflow |
| Rapid control prototyping | dSPACE MicroAutoBox II |
| Vehicle communication | LIN |
| Testing and monitoring | dSPACE ControlDesk, functional testing |
| Development workflow | Git, Jira |

## Results and Conclusion

The internship resulted in a functioning **hardware–software prototyping setup** for developing and testing EV climate-control functions. Testing demonstrated the operation of stepper drivers and the blower through the prototype environment.

This project strengthened my experience in automotive embedded systems, model-based development, LIN communication, real-time prototyping, integration, and functional testing.

## Project Documentation

This repository presents a concise overview of the internship work. The original company software, Simulink models, LIN configuration files, measurement data, and internal system diagrams are not published here.
