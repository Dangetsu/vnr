/** bootstrap.js
 *  2/22/2013 jichi
 *  See: bootstrap.scss (2.x)
 */
.pragma library // stateless

var styles = {
  '': {}

  // Buttons
  , btn: {
    textColor: '#333'
    , startColor: '#fff' //'white'
    , stopColor: '#e6e6e6'
    , hoverColor: '#e6e6e6'
    , activeColor: '#ccc'
  }
  , 'btn btn-primary': {
    textColor: 'snow'
    , startColor: '#08c'
    , stopColor: '#04c'
    , hoverColor: '#04c'
    , activeColor: '#039'
  }
  , 'btn btn-warning': {
    textColor: 'snow'
    , startColor: '#fbb450'
    , stopColor: '#f89406'
    , hoverColor: '#f89406'
    , activeColor: '#c67605'
  }
  , 'btn btn-danger': {
    textColor: 'snow'
    , startColor: '#ee5f5b'
    , stopColor: '#bd362f'
    , hoverColor: '#bd362f'
    , activeColor: '#942a25'
  }
  , 'btn btn-success': {
    textColor: 'snow'
    , startColor: '#62c462'
    , stopColor: '#51a351'
    , hoverColor: '#51a351'
    , activeColor: '#408140'
  }
  , 'btn btn-info': {
    textColor: 'snow'
    , startColor: '#5bc0de'
    , stopColor: '#2f96b4'
    , hoverColor: '#2f96b4'
    , activeColor: '#24748c'
  }
  , 'btn btn-inverse': {
    textColor: 'snow'
    , startColor: '#444'
    , stopColor: '#222'
    , hoverColor: '#222'
    , activeColor: '#090909'
  }
}

// @param c string, @return Object
function style(c) {
  try { return styles[c] }
  catch (e) { return {} }
}

// EOF
