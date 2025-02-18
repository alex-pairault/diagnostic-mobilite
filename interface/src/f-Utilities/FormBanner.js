import React, { Component } from 'react';

import {c_gradient_reds} from '../a-Graphic/Colors'

class FormBanner extends React.Component {

  render() {

    return(
      <div className="row fixed-bottom" style={{backgroundColor: c_gradient_reds[1], zIndex: 5000}}>
       <div className="col">
         <p className="m-2 text-center">
           <a target="_blank" href={this.props.link}>
             {this.props.label}
           </a>
         </p>
       </div>
      </div>
    )
  }
}

export default FormBanner;
