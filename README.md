# file-history  
Keeps track of all files operated on in your bash sessions.  
You can show recent files, select one and that file will be opened in editor.  
works in gui and terminal environments and can be installed system wide or only for one user (locally).  

![demo](demo.gif)  

## usage:  
```files```     -> shows recent files, lets you select one and open selected in editor  
```files foo``` -> same but only shows files whos path contain 'foo'  
```files -h```  -> see this for more complex scenrios  

## installation  
```git clone https://github.com/vincemann/file-history```  
```cd file-history```  
```./install.sh gui|terminal local|system```  
  
## complex usage example:  
This showcases how this tool could be combined using i3.  
You could map a hotkey to executing ```files --action=clip --filter=popup```.  
This way when typing a command and you need a file to complete it, you can simply search for it in a popup and insert it:  

![demo](demo-complex.gif)  
