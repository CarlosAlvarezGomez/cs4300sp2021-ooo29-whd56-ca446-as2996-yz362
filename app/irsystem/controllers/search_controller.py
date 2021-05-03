from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from flask import Response

# import
import json
import pandas as pd
import os
import ast
from . import descSimilarity as SIM # IMPORT SIMILARITY FUNCTION
from . import ingredients as IG # IMPORT INGREDIENTS FUNCTION
import numpy as np
import pickle5 as pickle


project_name = "Ilan's Cool Project Template"
net_id = "Ilan Filonenko: if56"

# read recipe database
# we will want to have a data structure that stores the eco footprint of each recipe, I assume it's in the recipes df for now
global inverted_index
global recipes
recipes = pd.read_csv('app/irsystem/controllers/Dataset/files/sampled_recipes.csv',index_col='id')
inverted_index = SIM.make_inverted_index(recipes)

global recipe_ids
recipe_ids = list(recipes.index)

global reviews
reviews = pd.read_csv('app/irsystem/controllers/Dataset/files/sampled_reviews.csv')

global agg_review_info
agg_review_info = pd.DataFrame(reviews.groupby('recipe_id').agg({'recipe_id':'count','rating':'mean'})).rename(columns={'recipe_id':'count'})

# calculate ecological ranking
global ecoDF
global ecoRankedList
global ecoRank
ecoDF = IG.get_recipe_co2_df()
ecoRankedList = list(ecoDF['id'])
#ecoDF = ecoDF.set_index('id')
ecoRank = {id:rank for rank,id in enumerate(ecoRankedList)}

# clustering
global most_sim_recipes
with open('app/irsystem/controllers/Dataset/files/most_sim_recipes.pkl', 'rb') as handle:
    most_sim_recipes = pickle.load(handle)

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
	dietReq = request.args.get('diet_req')    # get diet requirements
	description = request.args.get('recipe-description') # get description
	data = []

	if (not description):
		output_message = "Please input ingredients or a description to find ecologically friendly recipes! At the mean time, here are some well loved recipes that also save our planet: "

		# set weights
		ecoW = (float(maxFootprint)/80)*0.4
		ratingW = 1-ecoW

		# recipes sorted by rating
		sorted_review_info = agg_review_info.sort_values(['rating'], ascending=[False])
		rated_recipes = list(sorted_review_info.index)
		reviewRank = {id:rank for rank,id in enumerate(rated_recipes)}

		finalRank = {}
		for recipe in recipe_ids:
			
			if recipe in ecoRank.keys() and recipe in reviewRank.keys():

				if float(recipes.loc[recipe, 'minutes']) <= float(maxTime): 
					finalRank[recipe] = ecoW*ecoRank[recipe] + ratingW*reviewRank[recipe]
		
		data = []
		reccomend = sorted(finalRank, key = lambda k:finalRank[k])[:100]
		reccomend = IG.first_n_filtered(reccomend,allergies,dietReq,9)
		
		output = {}
		rec = {}
		if len(reccomend)>0:
			for id in reccomend:
				rec[id] = {
					"name":recipes.loc[id,'name'],
					"ingredients": ast.literal_eval(recipes.loc[id,'ingredients']),
					"description":recipes.loc[id,'description'],
					"steps":ast.literal_eval(recipes.loc[id,'steps']),
					"emission":round(float(ecoDF[ecoDF['id']==id]['CO2']), 2),
					"n_reviews":int(agg_review_info.loc[id,'count']),
					"avg_rating":round(agg_review_info.loc[id,'rating'],2),
					"degree":'second'
					}
		
		return render_template('results.html', name=project_name, netid=net_id, output_message=output_message, data=rec)

	else:
		output_message = "Your results: "

		# calculate description ranking
		descripList = SIM.get_cosine_similarities(description, inverted_index)
		# descripRankedList = list(descripDF['recipe_id'])
		# descripRank = {id:rank for rank,id in enumerate(descripRankedList)}
		descripKeys = descripList.keys()
		descripRank = {id:rank for rank,id in enumerate(descripKeys)}
		
		# set weights
		ecoW = (float(maxFootprint)/80)*0.4
		descripW = 1-ecoW

		# finalRanking
		finalRank = {}

		for recipe in recipe_ids:
			# just in case we didn't return all recipe ids, check if we have both scores first
			if recipe in ecoRank.keys() and recipe in descripRank.keys():

				# if the recipe meets time requirements
				if float(recipes.loc[recipe, 'minutes']) <= float(maxTime): #and float(recipes.loc[recipe,'emission']) <= maxFootprint:
					finalRank[recipe] = ecoW*ecoRank[recipe] + descripW*descripRank[recipe]
					# finalRank[recipe] = descripRank[recipe]

		data = sorted(finalRank, key = lambda k:finalRank[k])[:100]
		data = IG.first_n_filtered(data,allergies,dietReq,15)

		# second degree search of recipes users may be interested in based on social information
		reccomend = []
		for id in data[:9]:
			rec = most_sim_recipes[id]
			if rec not in data:
				reccomend.append(rec)


		output = {}
		for id in data:
			output[id] = {
				"name":recipes.loc[id,'name'],
				"ingredients": ast.literal_eval(recipes.loc[id,'ingredients']),
				"description":recipes.loc[id,'description'],
				"steps":ast.literal_eval(recipes.loc[id,'steps']),
				"emission":round(float(ecoDF[ecoDF['id']==id]['CO2']), 2),
				"n_reviews":int(agg_review_info.loc[id,'count']),
				"avg_rating":round(agg_review_info.loc[id,'rating'],2),
				"degree":'first'
				}

		rec = {}
		if len(reccomend)>0:
			for id in reccomend:
				rec[id] = {
					"name":recipes.loc[id,'name'],
					"ingredients": ast.literal_eval(recipes.loc[id,'ingredients']),
					"description":recipes.loc[id,'description'],
					"steps":ast.literal_eval(recipes.loc[id,'steps']),
					"emission":round(float(ecoDF[ecoDF['id']==id]['CO2']), 2),
					"n_reviews":int(agg_review_info.loc[id,'count']),
					"avg_rating":round(agg_review_info.loc[id,'rating'],2),
					"degree":'second'
					}

		return render_template('results.html', name=project_name, netid=net_id, output_message=output_message, data=output, recommendation=rec)
