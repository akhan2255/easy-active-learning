import numpy as np
import scipy.optimize as opt
from sklearn.metrics.pairwise import pairwise_distances
import kmedoids
from scipy.spatial import ConvexHull

def volume_objective_psi(psi_set, w_samples, delta_samples):
    dR = w_samples.dot(psi_set.T)
	p1 = 1/(1+np.exp(delta_samples - dR))
	p2 = 1/(1+np.exp(delta_samples + dR))
	p_Upsilon = (np.exp(2*delta_samples) - 1) * p1 * p2
	return p1.sum(axis=0)**2 + p2.sum(axis=0)**2 + p_Upsilon.sum(axis=0)**2
	
def information_objective_psi(psi_set, w_samples, delta_samples):
	M = w_samples.shape[0]
	dR = w_samples.dot(psi_set.T)
	p1 = 1/(1+np.exp(delta_samples - dR))
	p2 = 1/(1+np.exp(delta_samples + dR))
	p_Upsilon = (np.exp(2*delta_samples) - 1) * p1 * p2
	
	return 1.0/M * (np.sum(p1*np.log2(M*p1 / p1.sum(axis=0)), axis=0) + np.sum(p2*np.log2(M*p2 / p2.sum(axis=0)), axis=0) + np.sum(p_Upsilon*np.log2(M*p_Upsilon / p_Upsilon.sum(axis=0)), axis=0))

def generate_psi(simulation_object, inputs_set):
    z = simulation_object.feed_size
    inputs_set = np.array(inputs_set)
    if len(inputs_set.shape) == 1:
        inputs1 = inputs_set[:z].reshape(1,z)
        inputs2 = inputs_set[z:].reshape(1,z)
        input_count = 1
    else:
        inputs1 = inputs_set[:,:z]
        inputs2 = inputs_set[:,z:]
        input_count = inputs_set.shape[0]
    d = simulation_object.num_of_features
    features1 = np.zeros([input_count, d])
    features2 = np.zeros([input_count, d])
    for i in range(input_count):
        simulation_object.feed(list(inputs1[i]))
        features1[i] = simulation_object.get_features()
        simulation_object.feed(list(inputs2[i]))
        features2[i] = simulation_object.get_features()
    psi_set = features1 - features2
    return psi_set

def volume_objective(inputs_set, *args):
    simulation_object = args[0]
    w_samples = args[1]
	delta_samples = args[2]
    psi_set = generate_psi(simulation_object, inputs_set)
    return volume_objective_psi(psi_set, w_samples, delta_samples)
	
def information_objective(inputs_set, *args):
    simulation_object = args[0]
    w_samples = args[1]
	delta_samples = args[2]
    psi_set = generate_psi(simulation_object, inputs_set)
    return information_objective_psi(psi_set, w_samples, delta_samples)

def optimize(simulation_object, w_samples, delta_samples, func):
    z = simulation_object.feed_size
    lower_input_bound = [x[0] for x in simulation_object.feed_bounds]
    upper_input_bound = [x[1] for x in simulation_object.feed_bounds]
    opt_res = opt.fmin_l_bfgs_b(func, x0=np.random.uniform(low=2*lower_input_bound, high=2*upper_input_bound, size=(2*z)), args=(simulation_object, w_samples, delta_samples), bounds=simulation_object.feed_bounds*2, approx_grad=True)
    return opt_res[0][0:z], opt_res[0][z:2*z]

def volume(simulation_object, w_samples, delta_samples):
    return optimize(simulation_object, w_samples, delta_samples, volume_objective)
	
def information(simulation_object, w_samples, delta_samples):
    return optimize(simulation_object, w_samples, delta_samples, information_objective)

def random(simulation_object):
    lower_input_bound = [x[0] for x in simulation_object.feed_bounds]
    upper_input_bound = [x[1] for x in simulation_object.feed_bounds]
    input_A = np.random.uniform(low=2*lower_input_bound, high=2*upper_input_bound, size=(2*simulation_object.feed_size))
    input_B = np.random.uniform(low=2*lower_input_bound, high=2*upper_input_bound, size=(2*simulation_object.feed_size))
    return input_A, input_B
