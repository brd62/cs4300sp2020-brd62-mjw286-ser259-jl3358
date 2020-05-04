from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from app.irsystem.models.search import *
import pickle

project_name = "Course4me"
net_id = "Brady Dickens (brd62), Micah Wallingford (mjw286), Sam Rosenthal (ser259), Julian Londono (jl3358)"

classes_dict = pickle.load(open( "./class_roster_api_dict.pickle", "rb"))
classes_list = set()
majors_list = set()
for class_key in classes_dict.keys():
	for class_name in classes_dict[class_key]["subject-number"]:
		classes_list.add(class_name.upper())

		splitted = class_name.upper().split()
		majors_list.add(splitted[0])

classes_list = list(classes_list)
classes_list.sort()
majors_list = list(majors_list)
majors_list.sort()


@irsystem.route('/', methods=['GET'])
def search():
	
	relevant_ids = [int(request.args[key].split("-")[1])
						for key in request.args.keys() if "radiobox" in key and 
						request.args[key].split("-")[0] == "relevant"]
						
	irrelevant_ids = [int(request.args[key].split("-")[1]) 
						for key in request.args.keys() if "radiobox" in key and 
						request.args[key].split("-")[0] == "irrelevant"]
					
	original_query = ''
	keyword_query = request.args.get('keyword_search')
	# professor_query = request.args.get('professor_search')
	class_query = request.args.get('class_search')
	suggestion = request.args.get('suggestion_search')
	rocchio_update_query = request.args.get('rocchio_update_query')

	classLevel_query = request.args.get('class_level_search')
	semester_query = request.args.get('semester_search')
	major_query = request.args.get('major_search')

	if(suggestion):
		keyword_query = suggestion

	if keyword_query and not rocchio_update_query:
		data = getKeywordResults(keyword_query, classLevel_query, semester_query, major_query)
		suggestions = getSuggestions(keyword_query)
		original_query = keyword_query
		if len(data) > 0 :
			output_message = "Results for \"" + keyword_query + "\"" 
		else:
			output_message = "No results found for \"" + keyword_query + "\""

		if classLevel_query != None and classLevel_query !="":
			output_message += '\n' + "Class levels in the range [" + classLevel_query+"]"
		if semester_query != None and semester_query !="":
			output_message += '\n' + "Classes in the " + semester_query+" semester"
		if major_query != None and major_query !="":
			output_message += '\n' + "Classes in the " + major_query+" major"

		
	elif class_query and not rocchio_update_query:
		data = getClassResults(class_query)
		suggestions = []
		original_query = class_query

		if len(data) > 0 :
			output_message = "Results for "+ class_query
		else:
			output_message = "No results found for \"" + keyword_query + "\""
	elif rocchio_update_query:
		
		new_query = rocchio(rocchio_update_query, relevant_ids, irrelevant_ids)
		
		print(new_query)
		
		data = getKeywordResults(new_query, classLevel_query=None, semester_query=None, major_query=None)
		suggestions = getSuggestions(new_query)
		if len(data) == 0 :
			output_message = "No results found for \"" + keyword_query + "\"" + " after Rocchio Update"
			original_query = keyword_query
		else:
			output_message = "Updated Rocchio Results for \"" + new_query + "\""
			original_query = new_query
	
	
	else:
		data = []
		suggestions = []
		output_message = ''

	return render_template('search.html', name=project_name, netid=net_id,
							output_message=output_message, data=data, suggestions= suggestions,
							classes_list=classes_list, majors_list=majors_list,
							ogKeyword_query = original_query, ogClassLevel_query = classLevel_query,
							ogSemester_query = semester_query,ogMajor_query = major_query )
