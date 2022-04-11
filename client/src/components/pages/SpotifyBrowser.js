import { Component, createRef } from "react";
import { Col, Form, Row } from "react-bootstrap";
import SpotifyConnector from "../../managers/spotify";

class SpotifyBrowser extends Component {
  constructor(props) {
    super();
    this.spotify = new SpotifyConnector(
      "eb9d9961d9ea426fba452ff3cc947ae0",
      "23297c90f6804bbfb1fefcd5d4565a65"
    );
  }

  itemSelectedHandler(id, type) {
    console.log("Selected item", id, type);
  }

  render() {
    return (
      <div>
        <SearchBox spotify={this.spotify} onSelect={this.itemSelectedHandler} />
      </div>
    );
  }
}

class SearchBox extends Component {
  /** @type {SpotifyConnector} */
  spotify;

  /** @type {String} */
  queryHint = "Press Tab key to enable suggestions...";

  /** @type {state} */
  state = {
    input: "",
    type: "track",
    queryData: [{ value: this.queryHint }],
    datalistBindId: "datalist-" + Math.random()
  }

  constructor(props) {
    super();
    this.spotify = props.spotify;

    this.itemSelectedCallback = props.onSelect;

    this.queryInputKeyDownHandler = this.queryInputKeyDownHandler.bind(this);
    this.queryInputSelectHandler = this.queryInputSelectHandler.bind(this);
    this.queryInputSubmitHandler = this.queryInputSubmitHandler.bind(this);
    this.queryInputChangeHandler = this.queryInputChangeHandler.bind(this);

    this.queryTypeChangeHandler = this.queryTypeChangeHandler.bind(this);

    this.showSuggestions = this.showSuggestions.bind(this);

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
        console.log(items);
        this.setState({ queryData: items.map(item => ({ id: item.id, value: item.name })) })
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
              <Form.Control
                list={this.state.datalistBindId}
                placeholder="Type your query here..."
                autoComplete="off"
                onKeyDown={this.queryInputKeyDownHandler}
                onSelect={this.queryInputSelectHandler}
                onSubmit={this.queryInputSubmitHandler}
                onChange={this.queryInputChangeHandler} />
              <Form.Text className="text-muted">
                Press 'Tab' to get results from Spotify.
              </Form.Text>
              <Datalist id={this.state.datalistBindId} data={this.state.queryData} />
            </Form.Group>
          </Col>
        </Row>
      </Form>
    );
  }
}

function Datalist(props) {
  console.log("Datalist", props);
  return (
    <datalist id={props.id}>
      {props.data.map(item => <option key={item.id} value={item.id}>{item.value}</option>)}
    </datalist>
  )
}

class TrackDetail extends Component {
  constructor(props) {
    super();
  }

}

export default SpotifyBrowser;
