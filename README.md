# reactCodeGenerater 

this project helps speed up the react development
the code generator action , config, constants, index , reducers, selectors, css files for each container
the code is structured in a class for generating the files and some help function for generating blocks of code ,functions ,  
## get started
this instructions will help u get the project running
### Prerequisites
for each container you need a json file  with the info.json format
```
"projectPath":"redhorn-react/src/",
  "container" : "containers/",
  "formAlias":"game",
  "basePath":"Request",
  "action":[
    "request","response", "error", "cleanup"
  ],
  "formStruct":["breadcrumb","pageHead","formBody"],
  "props": ["loading","error"]
```

 * projectPath: where the redhorn-react project is located 
 * container: root path after src
 * formAlias: your form alias (it is best with out (-))
 * basePath: the category the form is from
 * action: actions expected the form UI needs to perform 
 * formStruct: you can add different components 
 * props: elements connected with reducer 

## Running the tests
after cloning you can simply run 
```
python3 firstTry.py 
```
don't forget updating projectPath to your local react project

