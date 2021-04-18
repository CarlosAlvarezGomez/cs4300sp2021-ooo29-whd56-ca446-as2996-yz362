from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

# import pandas
import pandas as pd

project_name = "Ilan's Cool Project Template"
net_id = "Ilan Filonenko: if56"

# read recipe database
# we will want to have a data structure that stores the eco footprint of each recipe, I assume it's in the recipes df for now
recipes = pd.read_csv('../../../../Dataset/files/sampled_recipes.csv',index_col='id')
recipe_ids = list(recipes.index())


@irsystem.route('/', methods=['GET'])
def search():
	ingredients = request.args.get('PLACE HOLDER') # get list of ingredients
	maxFootprint = request.args.get('PLACE HOLDER') # get max footprint
	maxTime = request.args.get('PLACE HOLDER') # get time limits
	allergies = request.args.get('PLACE HOLDER') # get list of allergies
	dietReq = request.args.get('PLACE HOLDER') # get diet requirements
	description = request.args.get('PLACE HOLDER') # get description

	if (not ingredients) and (not description):
		data = []
		output_message = "Please input ingredients or a description to find ecologically friendly recipes!"
	else:
		# calculate ecological ranking
		ecoDF = INGREDIENTS_SIM(ingredients,allergies,dietReq)
		# ecoRankedList = list(ecoDF['recipe_id'])
		ecoRank = {id:rank for rank,id in enumerate(ecoRankedList)}

		# calculate description ranking
		descripDF = DESCRIPTION_SIM(description)
		#descripRankedList = list(descripDF['recipe_id'])
		descripRank = {id:rank for rank,id in enumerate(descripRankedList)}

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

		data = sorted{finalRank, key = lambda k:finalRank[k]}[:20]


	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)
