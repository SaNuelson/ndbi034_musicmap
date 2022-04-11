import { Component } from "react";
import { Form } from "react-bootstrap";
import { fillObject } from "../../utils/react_helpers";

class SearchBox extends Component {
  /** @type {SpotifyConnector} */
  spotify;

  constructor(props) {
    super();
    this.spotify = props.spotify;
    this.state = {
      input: "",
      type: "track",
    };

    this.itemSelectedCallback = props.onSelect;

    this.queryInputKeyDownHandler = this.queryInputKeyDownHandler.bind(this);
    this.queryInputSelectHandler = this.queryInputSelectHandler.bind(this);
    this.queryInputSubmitHandler = this.queryInputSubmitHandler.bind(this);
    this.queryInputChangeHandler = this.queryInputChangeHandler.bind(this);

    this.queryTypeChangeHandler = this.queryTypeChangeHandler.bind(this);

    this.showSuggestions = this.showSuggestions.bind(this);

    this.queryInput = (
      <Form.Control
        list="queryDatalist"
        placeholder="Type your query here..."
        autoComplete="off"
        onKeyDown={this.queryInputKeyDownHandler}
        onSelect={this.queryInputSelectHandler}
        onSubmit={this.queryInputSubmitHandler}
        onChange={this.queryInputChangeHandler}
      />
    );
    this.queryInputInfo = (
      <Form.Text className="text-muted">
        Press 'Tab' to get results from Spotify.
      </Form.Text>
    );
    this.queryTypeSelect = (
      <Form.Select
        id="queryTypeSelect"
        onChange={this.queryTypeChangeHandler}
        defaultValue="track"
      >
        <option value="playlist">Playlist</option>
        <option value="album">Album</option>
        <option value="artist">Artist</option>
        <option value="track">Track</option>
      </Form.Select>
    );
    this.queryDatalist = <datalist id="queryDatalist" />;
    this.queryHint = new Option("Press down key to enable suggestions...");
  }

  queryInputChangeHandler(event) {
    this.setState({ input: event.target.value });
  }

  queryTypeChangeHandler(event) {
    this.queryDatalist.innerHTML = "";
    this.setState({ type: event.target.value });
  }

  queryInputSubmitHandler(event) {
    event.preventDefault();
    this.queryInputSelectHandler();
  }

  queryInputSelectHandler() {
    this.itemSelectedCallback(this.state.input, this.state.type);
  }

  queryInputKeyDownHandler(event) {
    if (event.which === 9) {
      event.preventDefault();
      this.showSuggestions();
    }
  }

  showSuggestions() {
    console.log("Suggestions prompted...");
    let query = this.state.input;
    let type = this.state.type;
    if (!query) return;

    this.spotify
      .search(query, type)
      .then((res) => res.json())
      .then((obj) => {
        let items = obj[type + "s"].items;
        this.queryDatalist.innerHTML = "";
        for (let item of items) {
          let name = item.name;
          let id = item.id;
          this.queryDatalist.appendChild(new Option(id, name));
        }
      });
  }

  render() {
    return (
      <Form onSubmit={this.queryInputSubmitHandler}>
        <Row>
          <Col sm={3}>
            <Form.Group>
              <Form.Label>Search type</Form.Label>
              {this.queryTypeSelect}
            </Form.Group>
          </Col>
          <Col>
            <Form.Group>
              <Form.Label>Search query</Form.Label>
              {this.queryInput}
              {this.queryInputInfo}
              {this.queryDatalist}
            </Form.Group>
          </Col>
        </Row>
      </Form>
    );
  }
}

class TypeSelect extends Component {
  state = {
    options: [],
    value: undefined
  };

  callbacks = {
    typeChanged: undefined
  };

  constructor(props) {
    super();
    fillObject(this.state, props);
    fillObject(this.callbacks, props);

    this.typeChangedHandler = this.typeChangedHandler.bind(this);
  }

  typeChangedHandler(event) {
    this.setState({ value: event.target.value });
    if (this.callbacks.typeChanged)
      this.callbacks.typeChanged(event.target.value);
  }

  render() {
    const options = this.state.options.map(option => <option value={option} />);
    return (
      <Form.Select onChange={this.typeChangedHandler} value={this.state.value}>
        {options}
      </Form.Select>
    );
  }
}

class QueryInput extends Component {
  state = {
    /** @type {String} text to show in label */
    labelText: "Search query",
    /** @type {String} text to use as placeholder */
    placeholder: "Type your query here...",
    /** @type {String} name of key which calls 'fillPrompted */
    fillKey: "Tab",
    /** @type {String} current value of input */
    value: undefined
  }

  callbacks = {
    /** @type {function(String):void} called with input value upon change */
    queryChanged: undefined,
    /** @type {function(String):void} called with input value upon pressing fillKey */
    fillPrompted: undefined,
    /** @type {function(String):void} called with input value upon submitting (selecting from datalist or pressing Enter) */
    querySubmitted: undefined
  }

  constructor(props) {
    super();
    fillObject(this.state, props);
    fillObject(this.callbacks, props);
  }

  keyDownHandler(event) {
    if (event.key === this.state.fillKey && this.callbacks.fillPrompted)
      this.callbacks.fillPrompted(this.state.value);
  }

  selectHandler(event) {
    let newValue = event.target.value;
    this.setState({value: newValue});

    if (this.callbacks.queryChanged)
      this.callbacks.queryChanged(newValue);
  }

  submitHandler(event) {
    event.preventDefault();
    if (this.callbacks.querySubmitted)
      this.callbacks.querySubmitted(this.state.value);
  }

  render() {
    return (
      <Form.Group>
        <Form.Label>{this.state.labelText}</Form.Label>
        <Form.Control
        list="queryDatalist"
        placeholder={this.state.placeholder}
        autoComplete="off"
        onKeyDown={this.keyDownHandler}
        onSelect={this.selectHandler}
        onSubmit={this.submitHandler}
        onChange={this.changeHandler}
      />
      <Form.Text className="text-muted">
        Press '{this.state.fillKey}' to get results from Spotify.
      </Form.Text>
      <datalist id="queryDatalist" />
      </Form.Group>
    );
  }
}

export default SearchBox;
