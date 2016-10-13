
//polyfill for IE
if (!String.prototype.endsWith) {
  String.prototype.endsWith = function(searchString, position) {
      var subjectString = this.toString();
      if (typeof position !== 'number' || !isFinite(position) || Math.floor(position) !== position || position > subjectString.length) {
        position = subjectString.length;
      }
      position -= searchString.length;
      var lastIndex = subjectString.lastIndexOf(searchString, position);
      return lastIndex !== -1 && lastIndex === position;
  };
}

function getDname(domain_name, ext) {
    if(domain_name.endsWith("." + ext)){
        return domain_name;
    } else{
        return domain_name + "." + ext;
    }
                // return domain_name
}