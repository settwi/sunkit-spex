import numpy as np
import pandas as pd
from astropy.table import Table
from copy import copy

class Parameters:
    def __init__(self, parameter_names, rParams=False):
        """
        This class's job is to handle parameter tables. I.e., store status, value, bounds, and errors 
        of each model variable.

        Parameters
        ----------
        parameter_names : list of strings
                List of the names of the parameters to be in the table.

        rParams : bool
                Determines whether the table is for response (True) or model (False) parameters.
                Default: False

        Properties
        ----------
        param_name : list
                Returns list of parameter names.
        param_status : pandas.core.series.Series
                Displays the parameters and their Status (i.e., if the are free, frozen, or tied).
        param_value : pandas.core.series.Series
                Displays the parameters and their Value (i.e., float).
        param_bounds : pandas.core.series.Series
                Displays the parameters and their Bounds (i.e., (float,float)).
        param_error : pandas.core.series.Series
                Displays the parameters and their Error (i.e., (float-,float+)).
        to_astropy : astropy.table.table.Table
                Converts the pandas table into an astropy table while adding a 0th columns of the 
                parameter names.

        Attributes
        ----------
        self.parameter_info : pandas.DataFrame
                Parameter table. This is the object that is indexed when the class is indexed.
        states : list of strings
                Parameter fields ["Status", "Value", "Bounds", "Error"].
        param_names : list of strings
                List of parameter names.

        Examples
        --------
        # load in 2 spectra, rebin the count channels to have a minimum of 10 counts then undo that rebinning
        pt = Parameters(["p1_spectrum1", "p2_spectrum1", "p1_spectrum2", "p2_spectrum2"])
        >>> pt
                      Status  Value       Bounds       Error
        p1_spectrum1    free    1.0  (0.0, None)  (0.0, 0.0)
        p2_spectrum1    free    1.0  (0.0, None)  (0.0, 0.0)
        p1_spectrum2    free    1.0  (0.0, None)  (0.0, 0.0)
        p2_spectrum2    free    1.0  (0.0, None)  (0.0, 0.0)

        pt["p1_spectrum1"] = "fixed" 
        # <equivalent> pt["Status", "p1_spectrum1"] = "fixed"
        # <equivalent> pt["p1_spectrum1", "Status"] = "fixed"
        # <equivalent> pt["Status"] = {"p1_spectrum1":"fixed"}
        # <equivalent> pt["Status"] = ["fixed", "free", "free", "free"]
        >>> pt
                      Status  Value       Bounds       Error
        p1_spectrum1  frozen    1.0  (0.0, None)  (0.0, 0.0)
                                ...

        # Freeze parameters with ("frozen", "freeze", "chill", "fix", "fixed", "secure", "stick", "glue", "preserve", "restrain", "restrained", "cannot_move", "cant_move", "canny_move", "married")    
        # Free parameters with ("free", "thaw", "loose", "unrestrained", "release", "released", "can_move", "single")   
        # Tie parameters with ("tie", "tied", "bind", "tether", "join", "joined", "in_a_relationship_with") followed by "_p1_spectrum1" or set to pt["p1_spectrum1"]        

        # To set value, change "Status" to "Value" and set to a float instead of string
        # To set bounds, change "Status" to "Bounds" and set to a tuple (minfloat,maxfloat) instead of string

        # To change multiple entries for one parameter
        pt["p1_spectrum1"] = {"Status":"fixed", "Value":4, "Bounds":(1, 50)} 
        # <equivalent>  pt["p1_spectrum1"] = ["fixed", 4, (1, 50)])
        >>> pt
                      Status  Value       Bounds       Error
        p1_spectrum1  frozen    4.0      (1, 50)  (0.0, 0.0)
                                ...
        """

        self._construction_string_parameters = f"Parameters({parameter_names},rParams={rParams})"
        # Ordinary params, default all free, value 1. Response params, default frozen and value 1 (gain) and 0 (offset)
        if not rParams:
            stat = ["free"]*len(parameter_names)
            params = np.ones(len(parameter_names))
            param_bounds = [(0.0, None)]*len(parameter_names) # None is no bounds for scipy
            param_errors = [(0.0, 0.0)]*len(parameter_names)
        else:
            stat = ["frozen"]*len(parameter_names)
            params = [1.0, 0.0]*int(len(parameter_names)/2)
            param_bounds = [(0.8, 1.2), (-0.1, 0.1)]*int(len(parameter_names)/2)
            param_errors = [(0.0, 0.0)]*len(parameter_names)
        
        self.states = ["Status", "Value", "Bounds", "Error"] # attributes of each param
        # make the columns of the parameter table
        self.param_names = parameter_names
        status = dict(zip(self.param_names, stat))
        values = dict(zip(self.param_names, params))
        bounds = dict(zip(self.param_names, param_bounds))
        errors = dict(zip(self.param_names, param_errors))
        # create table
        self.parameter_info = pd.DataFrame(dict(zip(self.states, [status, values, bounds, errors])))
        
        
    @property
    def param_name(self):
        ''' ***Property*** 
        Easily see the parameters located in the table.

        Parameters
        ----------

        Returns
        -------
        List of parameters.
        '''
        return list(self.parameter_info.index)
    
    @property
    def param_status(self):
        ''' ***Property*** 
        Easily see the parameter statuses (free, frozen, tied) located in the table.

        Parameters
        ----------

        Returns
        -------
        pandas.core.series.Series.
        '''
        return self.parameter_info["Status"]
    
    @property
    def param_value(self):
        ''' ***Property*** 
        Easily see the parameter values located in the table.

        Parameters
        ----------

        Returns
        -------
        pandas.core.series.Series.
        '''
        return self.parameter_info["Value"]
    
    @property
    def param_bounds(self):
        ''' ***Property*** 
        Easily see the parameter bounds for fitting located in the table.

        Parameters
        ----------

        Returns
        -------
        pandas.core.series.Series.
        '''
        return self.parameter_info["Bounds"]
    
    @property
    def param_error(self):
        ''' ***Property*** 
        Easily see the parameter errors located in the table.

        Parameters
        ----------

        Returns
        -------
        pandas.core.series.Series.
        '''
        return self.parameter_info["Error"]
    
    @property
    def to_astropy(self):
        ''' ***Property*** 
        Converts and returns the pandas data table (self.parameter_info) as an stropy table.

        Parameters
        ----------

        Returns
        -------
        astropy.table.table.Table.
        '''
        astropy_table = Table.from_pandas(self.parameter_info)
        astropy_table.add_column(self.param_name, name="Param", index=0)
        astropy_table["Bounds"].unit, astropy_table["Error"].unit = "(min, max)", "(-, +)"
        return astropy_table
    
    def get_spectrum_params(self, spectrum):
        # A method to return the parameters/rparameters of the given spectrum
        pass
    
    def _alternative_name(self, _for):
        ''' Stores the accepted synonyms for the Status state in the parameter table.

        Parameters
        ----------
        _for : str
                The status value that the synonyms are needed for.
                Need "frozen", "free", or "tie".

        Returns
        -------
        List of accepted synonyms.
        '''
        # the synonyms that the user can use to freeze, free, or tie parameter values
        if _for=="frozen":
            return ["frozen", "freeze", "chill", "fix", "fixed", "secure", "stick", "glue", "preserve", "restrain", "restrained", "cannot_move", "cant_move", "canny_move", "married"]
        elif _for=="free":
            return ["free", "thaw", "loose", "unrestrained", "release", "released", "can_move", "single"]
        elif _for=="tie":
            return ["tie", "tied", "bind", "tether", "join", "joined", "in_a_relationship_with"]
        
    def _frozen_free_or_tie(self, value):
        ''' Checks the value of the Status state, determines if it is a synonym of frozen, free, or is a tied parameter.
        The standard value of the Status is then returned. E.g., value="fixed" then return "frozen".

        Parameters
        ----------
        value : str
                A synonym of "frozen", "free", or "tie".

        Returns
        -------
        String of standard Status value.
        '''
        # check synonyms for frozen
        value = "frozen" if value.lower() in self._alternative_name(_for="frozen") else value
        # check synonyms for free
        value = "free" if value.lower() in self._alternative_name(_for="free") else value
        # check synonyms for tied
        for tie_syn in self._alternative_name(_for="tie"):
            if value.lower().startswith(tie_syn) and (value[len(tie_syn)+1:] in self.param_name):
                value = "tie"+value[len(tie_syn):]
                break
        return value
    
    def _check_valid_table(self):
        ''' Checks that all table values are valid and if not revert back to the original value.

        Parameters
        ----------

        Returns
        -------
        None.
        '''
        _invalid_str = "Invalid table element "
        # check status
        for i, s in zip(list(self.param_status.index), list(self.param_status)):
            if (s not in ("free", "frozen")) and (not str(s).startswith("tie")):
                print(_invalid_str, s, " for entry [Status, "+str(i)+"]. Must be \'free\', \'frozen\', or \'tie_paramName\' or accepted synonym. Changing back.")
                self.parameter_info.at[i, "Status"] = self._table_copy.at[i, "Status"]
        # check values
        for i, v in zip(list(self.param_value.index), list(self.param_value)):
            if (type(v) not in (int, float)):
                print(_invalid_str, v, " for entry [Value, "+str(i)+"]. Must be type int or float. Changing back.")
                self.parameter_info.at[i, "Value"] = self._table_copy.at[i, "Value"]
        # check Bounds
        for i, b in zip(list(self.param_bounds.index), list(self.param_bounds)):
            try:
                length = len(b) # must be 2
            except TypeError:
                length = 0 # this is because something that doesnt have __len__() method could be here which would cause a TypeError
            if (type(b) is not tuple) or (length!=2):
                print(_invalid_str, b, " for entry [Bounds, "+str(i)+"]. Must be type tuple of length 2, i.e., (min,max) with min<max. Changing back.")
                self.parameter_info.at[i, "Bounds"] = self._table_copy.at[i, "Bounds"]

    def _set_to_another_entry(self, item, new_value):
        ''' Handles what to do if a parameter table entry (param1) is set to another (param2).
        Param2's value will be tied to param1's value.

        Parameters
        ----------
        item : str
                Parameter name, state, or both. the entry(ies) to be changed
        
        new_value : pandas.core.series.Series
                Parameter table entry that the item parameter is to bve tied to.

        Returns
        -------
        None.

        Example
        -------
        # If you want to tie it to another param by setting one param entry to another
        self.parameter_info["param1"] = self.parameter_info["param2"]
        '''
        if (new_value.name in self.param_name) and (item!=new_value.name):
            self.parameter_info.at[item, "Status"] = "tie_"+new_value.name
        elif (new_value.name not in self.param_name):
            print("Parameter", new_value.name, "not in parameter table. Nothing is being changed.")
        elif (item==new_value.name):
            print("Tying parameter", item, "to itself (", new_value.name, ") would be equivalent to fixing this parameter. Nothing is being changed.")
        else:
            print("I don\'t know what you've set this to but nothing is being changed, sorry (", item, "=", new_value, ").")
    
    def _change_state(self, item, new_value):
        ''' Handles what to do if a state column in the param table is set to a list 
        or dictionary.

        Parameters
        ----------
        item : str
                State column in the param table to be changed.
        
        new_value : list or dict
                If dict then the keys need to be the parameters to be changed. 
                If list then the an entry needs to be provided for every parameter.

        Returns
        -------
        None.

        Example
        -------
        # If you want to change multiple entries in a state column (e.g., "Status)
        #  where the table has three parameters.
        #  with dict:
        self.parameter_info["Status"] = {"param1":"fixed", "param3":"fixed"}
        #  with list:
        self.parameter_info["Status"] = ["fixed", "free", "fixed"]
        '''
        if type(new_value) is dict:
            for key, val in new_value.items():
                val = self._frozen_free_or_tie(value=val) if (type(val) is str) else val
                self.parameter_info.at[key, item] = val
        elif type(new_value) is list:
            # check the list is the same length as the parameters
            assert len(self.param_names)==len(new_value), "List for column must be same legnth as parameters ("+str(len(self.param_names))+")."
            for key, val in zip(self.param_names, new_value):
                val = self._frozen_free_or_tie(value=val) if (type(val) is str) else val
                self.parameter_info.at[key, item] = val

    def _change_param(self, item, new_value):
        ''' Handles what to do if a parameter row in the param table is set to a list, 
        dictionary, string (change Status state), int/float (change Value state), or 
        tuple length==2 (change Bounds state).

        Parameters
        ----------
        item : str
                Parameter row in the param table to be changed.
        
        new_value : list or dict or str or int/float or tuple
                If dict then the keys need to be the states to be changed. 
                If list then any string, int/float, and tuple will change their 
                respective states.

        Returns
        -------
        None.

        Example
        -------
        # If you want to change multiple entries in a parameter row
        #  with dict:
        self.parameter_info["param1"] = {"Status":"fixed", "Value":4} 
        #  with list:
        self.parameter_info["param1"]=["fixed", 4]
        #  entries separately: 
        self.parameter_info["param1"]="fixed" 
        self.parameter_info["param1"]=4 
        '''
        if type(new_value) is dict:
            for key, val in new_value.items():
                val = self._frozen_free_or_tie(value=val) if (type(val) is str) else val
                self.parameter_info.at[item, key] = val
        else: #elif type(new_value) is list:
            new_value = _make_into_list(new_value)
            # check the list is the same length as the parameters
            for val in new_value:
                key = None
                val, key = (self._frozen_free_or_tie(value=val), "Status") if (type(val) is str) else (val, key) # is value given a string for the Status?
                val, key = (val, "Value") if (type(val) in (int, float)) else (val, key) # is value given a int/float for the Value?
                val, key = (val, "Bounds") if (type(val) is tuple) else (val, key) # is value given a tuple (length==2) for the Bounds?
                if type(key) is str:
                    self.parameter_info.at[item, key] = val
                else:
                    print(f"The value given ({val}) is not a valid parameter table input. Must be a string, int/float, or tuple length==2.")

    def _change_specfic_entry(self, item, new_value):
        ''' Handles what to do if indexed with two entries (a parameter and a state).

        Parameters
        ----------
        item : [str,str]
                [Parameter, State] or [State, Parameter] of the specific entry in the 
                param table to be changed.
        
        new_value : str or int/float or tuple
                The new value of the specific entry indicated by the item indices.

        Returns
        -------
        None.

        Example
        -------
        # index a specific entry in the table
        self.parameter_info["param1", "Status"] = "free"
        # <equivalent> self.parameter_info["Status", "param1"] = "free"
        '''
        # check both indices are in either param_names or states
        if (item[0] in self.param_names+self.states) and (item[1] in self.param_names+self.states):
            # if first index isn't the param name, assume the second one is
            index = item[0] if (item[0] in self.param_names) else item[1]
            col = list(item) 

            # remove the suspected param name from the indices
            col.remove(index) 

            # now get default string for the state if it is for the Status, else just leave it
            new_value = self._frozen_free_or_tie(value=new_value) if (type(new_value) is str) else new_value
            try:
                self.parameter_info.at[index, col[0]] = new_value # try to update the specific entry with .at[param_name,state]
            except KeyError:
                print("Indices need to be one from a row and one a column if two are given.")  

    def __setitem__(self, item, new_value):
        ''' The point in this class. Allows the parameter table entries to be set 
        a large number of ways as is convenient to the user.
        '''
        # create a table copy to store all original values
        self._table_copy = copy(self.parameter_info)
        
        # if you want to tie it to another param by setting one param entry to another (e.g., self.parameter_info["param1"]=self.parameter_info["param2"])
        if (type(new_value)==type(self["Status"])):
            self._set_to_another_entry(item, new_value)
        
        # set param vals by state (e.g., self.parameter_info["Status"]={"param1":"fixed", "param2":"free"} or self.parameter_info["Value"]=[5, 8] for 2 params)
        elif item in self.states:
            self._change_state(item, new_value)
            
        # set param vals by param name (e.g., self.parameter_info["param1"]={"Status":"fixed", "Value":4} or self.parameter_info["param1"]=["fixed", 4, (2,10)])
        # also e.g., self.parameter_info["param1"]="fixed" or self.parameter_info["param1"]=4, if set to str -> update Status, set to int/float -> update Value, etc. 
        elif item in self.param_names:
            self._change_param(item, new_value)
        
        # index a specific entry in the table, e.g., self.parameter_info["param1", "Status"]="free" or elf.parameter_info["Status", "param1"]="free"
        elif len(set(item))==2:
            self._change_specfic_entry(item, new_value)  
                    
        else:
            print("Invalid index ", item, ". Valid rows and column names are: ", self.param_names, " and ", self.states, ", respectively.")
            print("Or invalid value ", new_value, ". You have not set the parameter to a list, dict, string, integer, float, tuple (len==2), or row of itself.")
        self._check_valid_table() # check all entries are valid, if not then change back to original
        del self._table_copy # remove original table copy
        
    def __getitem__(self, item):
        ''' Allow the parameter table to be indexed by the state, parameter name, or both.'''
        if item in self.states:
            return self.parameter_info[item]
        elif item in self.param_names:
            return self.parameter_info.loc[item]
        elif len(set(item))==2:
            if (item[0] in self.param_names+self.states) and (item[1] in self.param_names+self.states):
                index = item[0] if (item[0] in self.param_names) else item[1]
                col = list(item)
                col.remove(index)
                try:
                    return self.parameter_info.at[index, col[0]]
                except KeyError:
                    print("Indices need to be one from a row and one a column if two are given.")
        print("Invalid index: ", item)
            
    def __repr__(self):
        '''Usually provide a representation to construct the class from scratch. However, when doing 
        .params in the child class we actually want to see the table itself. The user isn't expected 
        to use this class directly but if they do they can look at self._construction_string_parameters.'''
        # default for __str__() too if it's not here
        return f"{self.parameter_info}"

    def __str__(self):
        '''Provide a printable, user friendly representation of what the class contains.'''
        return f"{self.parameter_info}"

def _make_into_list(possible_list):
    ''' Tries to convert and return the possible_list  as a list.

    Parameters
    ----------
    item : optional
            Object to be turned into a list. If string or tuple then this will just 
            return [string] or [tuple], respectively. If not string or tuple but 
            iterable then returns list(possible_list) else [possible_list].

    Returns
    -------
    List.

    Example
    -------
    # index a specific entry in the table
    self.parameter_info["param1", "Status"] = "free"
    # <equivalent> self.parameter_info["Status", "param1"] = "free"
    '''
    # strings will be changes into a list as "asdf"-> ["a","s","d","f"]. Avoid this as want ["asdf"]
    # tuples can easily be converted to lists but want (2,4) ->[(2,4)]
    if (type(possible_list) is tuple) or (type(possible_list) is str):
        return [possible_list]
    try:
        return list(possible_list)
    except TypeError:
        return [possible_list]