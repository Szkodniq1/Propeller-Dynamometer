# Communication frame is written on 8 bits. In our protocol it can be either header frame or data frame.
# Each frame is specified on MSF bit which one it is. Header frame in addition on next four MSF bits
# have  written a function that communicate is dedicated to. It also specify what data will be send/recieved.
# Last three bits of header frame contains number of data frames that should be send. The data frame MSF bit is
# reserved and next seven bits are dedicated to send any data.

# MSF bit which decide whether it is a header frame or data frame
HEADER_FRAME = 0x00
DATA_FRAME = 0x80

# Header functions written on next four bits of header frame
START_TRANSMISSION = 0x00
STOP_TRANSMISSION = 0x08
CONNECTION = 0x10
EMERGENCY_STOP = 0x18
CALIBRATE_GET_VALUE = 0x20
CALIBRATE_SEND_PARAM_A = 0x28
CALIBRATE_SEND_PARAM_B = 0x60
SET_TEST_PARAMS = 0x30
START_TEST = 0x38
MEASURE = 0x40
STOP_TEST = 0x48


MODULE_ERROR = 0x78

# When module send MODULE_ERROR function, there is a specified error code instead of number of data frames send.
NO_TEST_PARAMETERS_ERROR = 0x00
WRONG_TEST_PARAMETERS_ERROR = 0x01

# Ready to send frames
START_TRANSMISSION_FRAME = HEADER_FRAME + START_TRANSMISSION
STOP_TRANSMISSION_FRAME = HEADER_FRAME + STOP_TRANSMISSION
CONNECTION_FRAME = HEADER_FRAME + CONNECTION
EMERGENCY_STOP_FRAME = HEADER_FRAME + EMERGENCY_STOP
START_TEST_FRAME = HEADER_FRAME + START_TEST
CALIBRATE_GET_VALUE_FRAME = HEADER_FRAME + CALIBRATE_GET_VALUE
CALIBRATE_SEND_PARAM_A_FRAME = HEADER_FRAME + CALIBRATE_SEND_PARAM_A
CALIBRATE_SEND_PARAM_B_FRAME = HEADER_FRAME + CALIBRATE_SEND_PARAM_B
MEASURE_FRAME = HEADER_FRAME + MEASURE

FRAME_MASK = 0x80
FUNCTION_MASK = 0x78
NUMBER_MASK = 0x07
DATA_MASK = 0x7F


def isHeader(data):
    if data < DATA_FRAME:
        return True
    else:
        return False


def isStartFrame(data):
    if data == START_TRANSMISSION_FRAME:
        return True
    else:
        return False


def isStopFrame(data):
    if data == STOP_TRANSMISSION_FRAME:
        return True
    else:
        return False


def sendEmergencyStop(serial):
    message = [START_TRANSMISSION_FRAME, EMERGENCY_STOP_FRAME, STOP_TRANSMISSION_FRAME]
    serial.write(message)


def sendConnected(serial):
    message = [START_TRANSMISSION_FRAME, CONNECTION_FRAME, STOP_TRANSMISSION_FRAME]
    serial.write(message)


def sendStartTest(serial):
    message = [START_TRANSMISSION_FRAME, START_TEST_FRAME, STOP_TRANSMISSION_FRAME]
    serial.write(message)


def sendGetValue(serial):
    message = [START_TRANSMISSION_FRAME, CALIBRATE_GET_VALUE_FRAME, STOP_TRANSMISSION_FRAME]
    serial.write(message)


def sendFunctionParameters(serial, a, b):
    firstParamData = convertFunctionParamToFrame(a)
    secondParamData = convertFunctionParamToFrame(b)
    message = [START_TRANSMISSION_FRAME, CALIBRATE_SEND_PARAM_A_FRAME + len(firstParamData)]
    message.extend(firstParamData)
    message.append(CALIBRATE_SEND_PARAM_B_FRAME + len(secondParamData))
    message.extend(secondParamData)
    message.append(STOP_TRANSMISSION_FRAME)
    serial.write(message)


def convertFunctionParamToFrame(param):
    message = []
    #sign
    if param < 0:
        message.append(0x81)
    else:
        message.append(0x80)
    #integer value
    number = int(param)
    if number < 0:
        number *= (-1)
    if number > 16383:
        lsfPart = number & 0x7F
        ssfPart = number >> 7
        ssfPart &= 0x7F
        msfPart = number >> 7
        message.append(DATA_FRAME+lsfPart)
        message.append(DATA_FRAME+ssfPart)
        message.append(DATA_FRAME+msfPart)
    elif number > 127:
        lsfPart = number & 0x7F
        msfPart = number >> 7
        message.append(DATA_FRAME+lsfPart)
        message.append(DATA_FRAME+msfPart)
    else:
        message.append(DATA_FRAME+number)
    #floating point value
    fract = (param - int(param)) * 1000
    if fract < 0:
        fract *= (-1)
    if fract < 127:
        message.append(DATA_FRAME+int(fract))
        message.append(0x80)
    else:
        lsfPart = int(fract) & 0x7F
        msfPart = int(fract) >> 7
        message.append(DATA_FRAME+lsfPart)
        message.append(DATA_FRAME+msfPart)

    return message


def sendTestParameters(serial, poleNumber, minPWM, maxPWM, jumpPWM, pwmTime):
    message = [START_TRANSMISSION_FRAME, SET_TEST_PARAMS+5, DATA_FRAME+poleNumber, DATA_FRAME+minPWM,
               DATA_FRAME+maxPWM, DATA_FRAME+jumpPWM, DATA_FRAME+pwmTime, STOP_TRANSMISSION_FRAME]
    serial.write(message)
