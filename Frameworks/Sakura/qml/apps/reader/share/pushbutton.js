/** pushbutton.js
 *  9/15/2014 jichi
 */
.pragma library // stateless

var styles = {
  '': {}

  // Buttons

  , 'inverse': {
    textColor: 'snow'
    , activeColor: '#aa434343' // black
    , disabledColor: '#aabebebe' // gray
  }

  , 'primary': {
    textColor: 'snow'
    , activeColor: '#aa00bfff' // blue
    , disabledColor: '#aabebebe' // gray
  }

  , 'success': {
    textColor: 'snow'
    , activeColor: '#aa00ff00' // green
    , disabledColor: '#aabebebe' // gray
  }

  , 'danger': {
    textColor: 'snow'
    , activeColor: '#aaff0000' // red
    , disabledColor: '#aabebebe' // gray
  }
}

// @param c string, @return Object
function style(c) {
  try { return styles[c] }
  catch (e) { return {} }
}

// EOF
