from ai_things import Generation
import pickle
import glob
from numpy import average

def generate_bot(desired_score):
    species_num = len(glob.glob(f"species/{desired_score}_v*"))
    current_gen = Generation()
    file = open(f"species/{desired_score}_v{species_num}.pickle", "wb")
    best_avg = 0
    #while score is still less than desired score
    while best_avg < desired_score:
        #train the generation
        current_gen.train()
        best_avg = average([comp.super_score for comp in current_gen.competitors])
        #update current gen to be the kids (can still access parent generations)
        current_gen = Generation(current_gen)
    print('Success')
    pickle.dump(current_gen, file)
    file.close()


generate_bot(10000)