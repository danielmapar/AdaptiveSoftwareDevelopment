def e(setpoint, process_variable):
    return setpoint - process_variable


def for_test():
    Kp = float(input("Enter Kp: "))
    Ki = float(input("Enter Ki: "))
    Kd = float(input("Enter Kd: "))
    K = float(input("Enter the constant: "))

    e_0 = float(input("Enter e(0): "))
    u = [e_0]

    setpoint = float(input("Enter setpoint: "))
    y_0 = float(input("Enter y(0): "))
    y = {0: y_0}

    T = int(input("Total time interval (2 is good): "))

    for t in range(1, T):
        e_t = e(setpoint, y[t - 1])
        u_t = (Kp * e_t) + (Ki * (e_t + sum(u))) + (Kd * (e_t - e(setpoint, y[t-1]))/T)
        u.append(u_t)

        y[t] = y[t - 1] + (K * u_t)
        print("u: {}, y: {}".format(u_t, y[t]))


if __name__ == "__main__":
    for_test()
