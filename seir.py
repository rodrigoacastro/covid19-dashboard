import numpy as np

class SeirModel:
    def __init__(self, t_max, infected, p):
        # Initial params for model calculation
        self.p = p
        self.t_max = t_max
        self.dt = .1
        self.t = np.linspace(0, self.t_max, int(self.t_max/self.dt) + 1)
        self.N = 200000000
        self.infected = infected
        self.exposed = (self.infected*15)
        self.init_vals = 1 - self.exposed/self.N, self.exposed/self.N, self.infected/self.N, 0
        alpha = 0.2
        beta = 1.2 * self.p
        gamma = 0.5
        self.params = alpha, beta, gamma

    def get_model_results(self):
        S_0, E_0, I_0, R_0 = self.init_vals
        S, E, I, R = [S_0], [E_0], [I_0], [R_0]
        alpha, beta, gamma = self.params
        dt = self.t[1] - self.t[0]
        for _ in self.t[1:]:
            next_S = S[-1] - (beta*S[-1]*I[-1])*dt
            next_E = E[-1] + (beta*S[-1]*I[-1] - alpha*E[-1])*dt
            next_I = I[-1] + (alpha*E[-1] - gamma*I[-1])*dt
            next_R = R[-1] + (gamma*I[-1])*dt
            S.append(next_S)
            E.append(next_E)
            I.append(next_I)
            R.append(next_R)

        results_stacked = np.stack([S, E, I, R]).T
        S = results_stacked[:, 0]
        E = results_stacked[:, 1]
        I = results_stacked[:, 2]
        R = results_stacked[:, 3]
        
        return S, E, I, R

