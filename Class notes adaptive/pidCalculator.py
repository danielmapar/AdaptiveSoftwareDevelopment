def e(setpoint, process_variable):
    return setpoint - process_variable

def for_test():
    Kp = float(input('Enter Kp: '))
    Ki = float(input('Enter Ki: '))
    Kd = float(input('Enter Kd: '))
    K = float(input('Enter the constant: '))

    e_0 = float(input('Enter e(0): '))
    u = [e_0]

    setpoint = float(input('Enter setpoint: '))
    y_0 = float(input('Enter y(0): '))
    y = {0: y_0}

    T = int(input('Total time interval (2 is good): '))

    for t in range(1, T):
        e_t = e(setpoint, y[t-1])
        u_t = (Kp * e_t) + (Ki * (e_t + sum(u))) + Kd
        u.append(u_t)

        y[t] = y[t-1] + (K * u_t)
        print("u: {}, y: {}".format(u_t, y[t]))

def question2():
    print("Question 2")

    Kp = 0.3
    Ki = 0.15
    Kd = 0
    K = 0.3

    u = [-6] # Utilizations
    setpoint = 10
    y = {0: 15} # Hashmap of response time for each second

    for t in range(1, 2):
        e_t = e(setpoint, y[t-1])
        u_t = (Kp * e_t) + (Ki * (e_t + sum(u))) + Kd
        u.append(u_t)

        y[t] = y[t-1] + (K * u_t)
        print("u: {}, y: {}".format(u_t, y[t]))

def question1():
    print("Question 1")

    Kp = 0.2
    Ki = 0
    Kd = 0

    setpoint = 10
    y = {0: 15} # Hashmap of response time for each second

    for t in range(1, 1):
        u_t = Kp * e(setpoint, y[t-1]) + Ki + Kd
        y[t] = y[t-1]+ (0.5*u_t)
        print("u: {}, y: {}".format(u_t, y[t]))

#question1()
#print("------")
#question2()
#print("------")
for_test()
