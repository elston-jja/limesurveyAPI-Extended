import base64
from collections import OrderedDict
from limesurveyrc2api.exceptions import LimeSurveyError


class _Survey(object):

    def __init__(self, api):
        self.api = api

    def list_surveys(self, username=None):
        """
        List surveys accessible to the specified username.

        Parameters
        :param username: LimeSurvey username to list accessible surveys for.
        :type username: String
        """
        method = "list_surveys"
        params = OrderedDict([
            ("sSessionKey", self.api.session_key),
            ("iSurveyID", username or self.api.username)
        ])
        response = self.api.query(method=method, params=params)
        response_type = type(response)

        if response_type is dict and "status" in response:
            status = response["status"]
            error_messages = [
                "Invalid user",
                "No surveys found",
                "Invalid session key"
            ]
            for message in error_messages:
                if status == message:
                    raise LimeSurveyError(method, status)
        else:
            assert response_type is list
        return response

    def _checkEmailFormat(self, email):
        method = "_checkEmailFomat"
        params = OrderedDict([
            ("sEmail", email)
        ])
        response = self.api.query(method=method, params=params)
        response_type = type(response)

        if response_type is bool:
            return response
        else:
            raise Exception("Error: Unable to validate email")

    def _checkSessionKey(self, sessionKey):
        method = "_checkSessionKey"
        params = OrderedDict([
            ("sSessionKey", sessionKey)
        ])
        response = self.api.query(method=method, params=params)
        response_type = type(response)

        if response_type is bool:
            return response
        else:
            raise Exception("Error: Unable to validate session key")

    def _doLogin(self, username, password, plugin):
        method= "_doLogin"
        params= OrderedDict([
            ("sUsername", username),
            ("sPassword", password),
            ("sPlugin", plugin)
        ])

        response = self.api.query(method=method, params=params)
        return response

    def activate_survey(survey_id):
        method= "activate_survey"
        params= OrderedDict([
            ("sSessionKey", self.api.session_key),
            ("iSurveyID", survey_id)
        ])
        
        response = self.api.query(method=method, params=params)
        return response

    def delete_survey(survey_id):
        method= "delete_survey"
        params= OrderedDict([
            ("sSessionKey", self.api.session_key),
            ("iSurveyID", survey_id)
        ])
        
        response = self.api.query(method=method, params=params)
        return response
        
    def get_survey_properties(self, survey_id):
        '''
        Modifications
        '''
        method = "get_survey_properties"
        params = OrderedDict([
            ("sSessionKey", self.api.session_key),
            ("iSurveyID", survey_id)
        ])

        response = self.api.query(method=method, params=params)
        response_type = type(response)

        '''No error handles'''
        return response

    def list_users(self):
        method = "list_users"
        params = OrderedDict([
            ("sSessionKey", self.api.session_key)
        ])

        response = self.api.query(method=method, params=params)
        return response

    def get_users_by_id(self):

        user_list = self.list_users()
        uid_user_dict = {}

        for user in user_list:
            del user['permissions']
            uid = user.pop('uid')
            user.pop('htmleditormode', None)
            user.pop('templateeditormode', None)
            user.pop('questionselectormode', None)
            
            uid_user_dict[uid] = user

        return uid_user_dict
    
    

    def export_responses(self, survey_id, document_type, language_code=None):
        '''
        API call for export_responses
        
        document types: "pdf", "csv", "xls", "doc", "json"
        '''
        
        method = "export_responses"
        params = OrderedDict([
            ("sSessionKey", self.api.session_key),
            ("iSurveyID", survey_id),
            ("sDocumentType", document_type),
            ("sLanguageCode", language_code)
        ])

        response = self.api.query(method=method, params=params)
        response_type = type(response)

        if response_type is dict and "status" in response:
            error_messages = [
                "No Data, survey table does not exist.",
                "No Data, could not get max id."
            ]
            if response["status"] in error_messages:
                return None

            else:
                raise Exception("Unexpected Error")
        
        return response
    

    def export_responses_to_file(self, survey_id, document_type,
                                 users_by_id=None, language_code=None):
        '''
        Exports the responses
        
        Parameters:
        survey_id: int
        document_type: string {pdf, csv, xml, json, doc}
        users_list: (optional, provides better filenames) list
        language_code: (optional, default English) string {en,...}

        users_list is the returned object from the API call list_users_by_uid
        '''
        
        response_data = self.export_responses(survey_id, document_type, language_code)

        if users_by_id is not None:
            properties = self.get_survey_properties(survey_id)
            owner_id = properties["owner_id"]           
            owner_details = users_by_id[str(owner_id)]

            filename = "{}_{}.{}".format(str(survey_id),
                                     str(owner_details["full_name"]),
                                    str(document_type))
        else:
            filename = "{}.{}".format(str(survey_id), str(document_type))

            
        if response_data is not None:
            responses  = (base64.b64decode(response_data)).decode("utf-8")


        else:
            responses = "No Response Data"
            

        # debugging info
        print("Wrote data to {}".format(filename))
            
        f = open(filename, "w")
        f.write(responses)
        f.close()        

    
    
        
    def list_questions(self, survey_id, group_id=None, language=None):
        """
        Return a list of questions from the specified survey.

        Parameters
        :param survey_id: ID of survey to list questions from.
        :type survey_id: Integer
        :param group_id: ID of the question group to filter on.
        :type group_id: Integer
        :param language: Language of survey to return for.
        :type language: String
        """
        method = "list_questions"
        params = OrderedDict([
            ("sSessionKey", self.api.session_key),
            ("iSurveyID", survey_id),
            ("iGroupID", group_id),
            ("sLanguage", language)
        ])
        response = self.api.query(method=method, params=params)
        response_type = type(response)
        
        if response_type is dict and "status" in response:
            status = response["status"]
            error_messages = [
                "Error: Invalid survey ID",
                "Error: Invalid language",
                "Error: IMissmatch in surveyid and groupid",
                "No questions found",
                "No permission",
                "Invalid session key"
            ]
            for message in error_messages:
                if status == message:
                    raise LimeSurveyError(method, status)
        else:
            assert response_type is list
        return response
