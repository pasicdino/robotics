import numpy as np
import math

class KalmanFilter:
    def __init__(self, initial_state, initial_covariance, process_noise, measurement_noise, robot, map):
        self.state = np.array(initial_state)  # State includes [x, y, orientation]
        self.covariance = np.array(initial_covariance)  # Initial covariance matrix
        self.process_noise = process_noise  # Process noise covariance matrix
        self.measurement_noise = measurement_noise  # Measurement noise covariance matrix
        self.path = [(self.state[0], self.state[1])]

        self.covariance_history = []    # holds ellipse properties from covariance matrices - [(x, y), (major-axis, minor-axis, angle)]

        self.robot = robot  # Reference to the robot object, assuming it holds map information
        self.map = map

    def predict(self, control_input, dt):
        x, y, theta = self.state

        v, omega = control_input

        # Predict new state based on the robot's control inputs
        dx = v * np.cos(theta) * dt
        dy = v * np.sin(theta) * dt
        dtheta = omega * dt

        # Update state
        x += dx
        y += dy
        theta = (theta + dtheta) % (2 * np.pi)  # Normalize orientation

        self.state = np.array([x, y, theta])

        # Update covariance with the correct Jacobian of the motion model
        F = np.array([
            [1, 0, -v * np.sin(theta) * dt],
            [0, 1,  v * np.cos(theta) * dt],
            [0, 0, 1]
        ])
        self.covariance = F @ self.covariance @ F.T + self.process_noise

    def update(self, measurements):
        for distance, bearing, feature in measurements:
            feature_x, feature_y = feature[0], feature[1]
            expected_distance, expected_bearing = self.calculate_expected_measurement(feature_x, feature_y)

            z_res = np.array([distance - expected_distance, bearing - expected_bearing])

            # Calculate the correct Jacobian H for the measurement function
            H = self.calculate_jacobian_H(feature_x, feature_y)

            # Compute the residual covariance
            S = H @ self.covariance @ H.T + self.measurement_noise

            # Calculate Kalman gain
            K = self.covariance @ H.T @ np.linalg.inv(S)

            # Update the state with the new measurement
            self.state += K @ z_res

            # Update the covariance
            self.covariance = (np.eye(len(self.state)) - K @ H) @ self.covariance

        self.path.append((self.state[0], self.state[1]))
        
        # every 100 steps: calculate covariance ellipse
        if len(self.path) % 100 == 0:
            self.covariance_history.append(((self.state[0], self.state[1]), self.calculate_covariance_ellipse(self.covariance)))

    def calculate_expected_measurement(self, feature_x, feature_y):
        x, y, theta = self.state
        dx = feature_x - x
        dy = feature_y - y
        distance = np.sqrt(dx**2 + dy**2)
        bearing = np.arctan2(dy, dx) - theta
        return distance, bearing

    def calculate_jacobian_H(self, feature_x, feature_y):
        x, y, theta = self.state
        dx = feature_x - x
        dy = feature_y - y
        d_squared = dx**2 + dy**2
        d = np.sqrt(d_squared)

        H = np.zeros((2, 3))
        H[0, 0] = -dx / d  # Partial derivative of distance with respect to x
        H[0, 1] = -dy / d  # Partial derivative of distance with respect to y
        H[1, 0] = dy / d_squared  # Partial derivative of bearing with respect to x
        H[1, 1] = -dx / d_squared  # Partial derivative of bearing with respect to y
        H[1, 2] = -1  # Partial derivative of bearing with respect to theta
        return H

    def calculate_covariance_ellipse(self, covariance):
        eigen_values, eigen_vectors = np.linalg.eigh(covariance)
        eigen_values = np.flip(eigen_values, 0)     # flip to decreasing order
        eigen_vectors = np.flip(eigen_vectors, 0)   # flip to decreasing order

        # calculate major and minor axis of covariance ellipse
        major_axis = 2 * np.sqrt(5.991 * eigen_values[0])
        minor_axis = 2 * np.sqrt(5.991 * eigen_values[1])

        # calculate angle of ellipse
        ellipse_angle = np.degrees(np.arctan2(eigen_vectors[1,0], eigen_vectors[0,0]))

        return major_axis, minor_axis, ellipse_angle
