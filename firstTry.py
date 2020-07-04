import copy
import json
import os
import jsbeautifier


files = ['config.js', 'constants.js', 'actions.js', 'selectors.js', 'reducers.js', 'index.js']


class ReactFileGenerator:

    def __init__(self, json_path="./info.json"):
        self.data = dict()
        self.read_json_file(json_path)
        self.react_path = self.data['projectPath']
        self.container = self.data['container']
        self.base_path = self.data['basePath']
        self.selectors = []
        self.actions = []
        self.alias = self.data['formAlias'].capitalize()
        self.path = self.react_path + self.container + self.base_path + '/' + self.alias
        self.create_directory(self.path)
        self.create_config()
        self.create_Constants()
        self.create_css()
        self.create_actions()
        self.create_selectors()
        self.create_reducer()
        self.create_index()
        self.format_file(files)
        pass

    def read_json_file(self, json_path):
        f = open(json_path)
        self.data = json.loads((f.read()))
        f.close()

    def create_directory(self, path):
        try:
            os.makedirs(path)
            print("folder was created in " + path)
        except OSError as error:
            print("file exsists")
            pass

    def create_config(self):
        f = open(self.path + "/config.js", "w")
        export_str = ""
        for i in self.data["formStruct"]:
            f.write("const " + i + " = ")
            write_block_code("", f)
            export_str = export_str + i + ",\n"
        f.write("export default")
        write_block_code(export_str, f)
        f.close()
        jsbeautifier.beautify_file(self.path + "/config.js", '__replace')

    def create_Constants(self):
        f = open(self.path + "/constants.js", "w")
        for action in self.data["action"]:
            f.write(
                'export const ' + action.upper() + "_" + self.alias.upper() + ' = "form/' +
                self.alias + "/" + action.upper() + '";\n')
            self.actions.append(action.upper() + "_" + self.alias.upper())
        f.close()
        jsbeautifier.beautify_file(self.path + "/constants.js", '__replace')
        pass

    def create_css(self):
        f = open(self.path + '/' + self.alias + '.css', "w")
        f.close()

    def create_actions(self):
        f = open(self.path + '/actions.js', "w")
        write_import(f, ["axios"], "axios", True)
        write_import(f, self.actions, "./constants")
        write_import(f, ["API"], "constants")
        write_import(f, ["BearerToken"], "token")
        for i in range(len(self.actions)):
            if self.data["action"][i] == "request" or self.data["action"][i] == "response":
                write_function(f, self.alias.lower() + self.data["action"][i].capitalize(),
                               "type: " + self.actions[i] + ",data ", ["data"])
            elif self.data["action"][i] == "error":
                write_function(f, self.alias.lower() + self.data["action"][i].capitalize(),
                               "type: " + self.actions[i] + ",error ", ["error"])
            else:
                write_function(f, self.alias.lower() + self.data["action"][i].capitalize(),
                               "type: " + self.actions[i], ["_"])
        f.close()
        jsbeautifier.beautify_file(self.path + '/actions.js', '__replace')

    def create_selectors(self):
        props = self.data["props"]
        f = open(self.path + '/selectors.js', "w")
        write_import(f, ["createSelector"], "reselect")
        write_function(f, "selectGlobal", "state." + self.base_path.lower() + "." + self.alias + "|| {};", ["state"],
                       False)
        exportstr = ""
        for prop in props:
            write_function(f, "makeSelect" + prop.capitalize(),
                           "createSelector(selectGlobal, (state) => state." + prop + ");", [], False)
            exportstr += "makeSelect" + prop.capitalize() + ",\n"
            self.selectors.append("makeSelect" + prop.capitalize())
        f.write("export ")
        write_block_code(exportstr, f)
        f.close()
        jsbeautifier.beautify_file(self.path + '/selectors.js', '__replace')

    def create_reducer(self):
        f = open(self.path + '/reducers.js', "w")
        write_import(f, self.actions, "./constants")
        write_import(f, ["produce"], "immer")
        write_import(f, ["checkUnauthorized"], "utils")
        write_function(f, self.alias + "Reducer", "", ["state = {}", "action"], False)
        f.write("produce(state, (draft) => {\n")
        f.write(" switch (action.type) {")
        for i in range(len(self.actions)):
            f.write("case " + self.actions[i] + ":\n")
            if self.data["action"][i] == "request":
                f.write(" draft.loading = true;\n")
            else:
                f.write(" draft.loading = false;\n")
            if self.data["action"][i] == "error":
                f.write(" draft.error = action.error;\n")
                f.write("checkUnauthorized(action);\n")
            f.write("  break;\n")
        f.write("default:\n")
        f.write("break;\n}\n});")
        f.write("export default " + self.alias + "Reducer" + ";\n")
        f.close()
        pass

    def create_index(self):
        f = open(self.path + '/index.js', "w")
        f.write('import React, { useEffect, memo, useState } from "react";\n')
        write_import_index(f, self.selectors)
        props = copy.deepcopy(self.data['props'])
        props[-1] = props[-1] + "}"
        write_function(f, self.alias, "", ["{history"] + props, False)
        write_block_code("", f)
        f.write(self.alias + ".propTypes = ")
        write_block_code(prop_type(self.data), f)
        f.write("const mapStateToProps = \n")
        f.write("createStructuredSelector({")
        for i in range(len(self.data['props'])):
            f.write(self.data['props'][i] + ": " + self.selectors[i] + "(),\n")
        f.write("});\n")
        write_function(f, "mapDispatchToProps", "dispatch", ["dispatch"])
        f.write("const withConnect = connect(mapStateToProps, mapDispatchToProps);\n")
        f.write("export default compose(withConnect, memo)(withRouter(" + self.alias + "));\n")
        f.close()
        jsbeautifier.beautify_file(self.path + '/index.js', '__replace')

    def format_file(self, file_list):
        for file in file_list:
            res = jsbeautifier.beautify_file(self.path + '/'+file)
            f = open(self.path + '/'+file, "w")
            f.write(res)
            f.close()


def prop_type(data):
    proptype = ''
    for prop in data['props']:
        proptype += prop + ": PropTypes."
        if prop == "loading":
            proptype += "bool,\n"
        else:
            proptype += "object,\n"
    return proptype


def write_import_index(f, selectors):
    write_import(f, ["PropTypes"], "prop-types", True)
    write_import(f, ["getPageTitle"], "utils")
    write_import(f, ["LoadingOverlay", "PageHead", "Breadcrumb", "ButtonService"], "components")
    write_import(f, ["withRouter"], "react-router-dom")
    write_import(f, ["compose"], "redux")
    write_import(f, ["connect"], "react-redux")
    write_import(f, [], "./actions")
    write_import(f, selectors, "./selectors")
    write_import(f, ["createStructuredSelector"], "reselect")
    write_import(f, ["config"], "./config", True)
    write_import(f, ["swal"], 'sweetalert', True)


def write_function(f, name, body, params, block=True):
    f.write("const " + name + "= (")
    for param in params:
        f.write(param)
        f.write(", ") if (param != params[-1]) else None
    if block:
        f.write(") => ({\n" + body + "});\n")
    else:
        f.write(") => " + body + "\n")
    pass


def write_block_code(body, f):
    f.write("{\n" + body + "};\n")


def write_import(f, package_name, path, parm=False):
    if len(package_name) == 1 and parm:
        f.write("import " + package_name[0] + ' from "' + path + '";\n')
    else:
        f.write("import {\n")
        for i in package_name:
            f.write(i + ",\n")
        f.write('} from "' + path + '";\n')


opts = jsbeautifier.default_options()
ReactFileGenerator()
