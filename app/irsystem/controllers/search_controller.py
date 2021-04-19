from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

# import
import json
import pandas as pd
import os
import descSimilarity as SIM# IMPORT SIMILARITY FUNCTION
import ingredients as IG # IMPORT INGREDIENTS FUNCTION


project_name = "Ilan's Cool Project Template"
net_id = "Ilan Filonenko: if56"

# read recipe database
# we will want to have a data structure that stores the eco footprint of each recipe, I assume it's in the recipes df for now
global inverted_index = SIM.make_inverted_index(pd.read_csv('../../../Dataset/files/sampled_recipes.csv'))
cwd = os.getcwd()
os.chdir("..")
os.chdir("..")
os.chdir("..")
global recipes = pd.read_csv('Dataset/files/sampled_recipes.csv',index_col='id')
global recipe_ids = list(recipes.index())
os.chdir(mycwd)

@irsystem.route('/')
def main():
	output_message = ''
	data = []
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)

@irsystem.route('/search', methods=['GET'])
def search():
	#ingredients = request.args.get('ingredients') # get list of ingredients
	maxFootprint = request.args.get('ecoSlide') # get max footprint
	maxTime = request.args.get('timeSlide') # get time limits
	allergies = request.args.get('allergies') # get list of allergies
	dietReq = request.args.getlist('diet_req')    # get diet requirements
	description = request.args.get('recipe-description') # get description

	if (not description):
		output = {}
		#output_message = "Please input ingredients or a description to find ecologically friendly recipes!"
	else:
		# calculate ecological ranking
		ecoDF = IG.get_recipe_co2_df()
		ecoRankedList = list(ecoDF['id'])
		ecoRank = {id:rank for rank,id in enumerate(ecoRankedList)}

		# calculate description ranking
		descripList = get_cosine_similarities(description, inverted_index)
		# descripRankedList = list(descripDF['recipe_id'])
		# descripRank = {id:rank for rank,id in enumerate(descripRankedList)}
		descripRank = descripList.keys()

		# set weights
		ecoW = 0.5
		descripW = 1-ecoW

		# finalRanking
		finalRank = {}

		for recipe in recipe_ids:
			# just in case we didn't return all recipe ids, check if we have both scores first
			if recipe in ecoRank.keys() and recipe in descripRank.keys():

				# if the recipe meets time and eco requirements
				if recipes[recipe,'minutes'] <= maxTime and recipes[recipe,'emission'] <= maxFootprint
					finalRank[recipe] = ecoW*ecoRank[recipe] + descripW*descripRank[recipe]

		data = sorted{finalRank, key = lambda k:finalRank[k]}[:100]
		data = IG.first_n_filtered(data,allergies,dietReq,20)

	output = {}

	for id in data:
		output{id} = {
		"ingredients": recipes[id,'ingredients'],
		"description":recipes[id,'description'],
		"steps":recipes[id,'steps']
		} # THIS WILL NEED TO TAKE IN ML COMPONENT RESULTS AND MAYBE FOORPRINT INFO?

	# return render_template('result.html', name=project_name, netid=net_id, output_message=output_message, data=data)
	return json.dumps(output)
