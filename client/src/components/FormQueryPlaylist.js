import React, { Component } from 'react';
import {Form, Button, ProgressBar} from 'react-bootstrap';
import MMSocket from '../utils/websocket.ts';

class FormQueryPlaylist extends Component {

  /** @type {MMSocket} */
  ws;

  constructor(props){
    super();
    this.state = {uri: '', progress: null};
    this.ws = props.ws;

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleProgress = this.handleProgress.bind(this);
    this.handleResponse = this.handleResponse.bind(this);
    this.onPlaylistAdded = props.onPlaylistAdded;
  }

  handleChange(ev) {
    this.setState({uri: ev.target.value});
  }

  handleSubmit(ev) {
    ev.preventDefault();
    console.log("Submit: ", this.state.uri);
    console.log("handle response", this.handleResponse);
    this.ws.get(this.state.uri, this.handleResponse, undefined, this.handleProgress);
  }

  handleProgress(percent) {
    this.setState({progress: percent});
  }

  handleResponse(data) {
    this.setState({progress: null});
    this.onPlaylistAdded(data);
  }

  render() {
    return (
      <Form action='new_playlist' method='POST'>
        <Form.Group controlId="uri">
          <Form.Label>Playlist URI</Form.Label>
          <Form.Control onChange={this.handleChange}></Form.Control>
          <Form.Text>URI of playlist to load and process</Form.Text>
        </Form.Group>
        <Button variant="primary" onClick={this.handleSubmit}>Send</Button>
        <ProgressBar now={this.state.progress}></ProgressBar>
      </Form>
    );
  }
}

export default FormQueryPlaylist;