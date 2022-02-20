import React, { Component } from "react";
import { Container, Nav, Navbar, Row, Col } from "react-bootstrap";
import FormQueryPlaylist from "./components/FormQueryPlaylist";
import TrackList from "./components/TrackList";
import "./App.css";
import DatabaseScreen from "./components/DatabaseTable";
import MMSocket from "./utils/websocket.ts";
import TestComponent from "./components/TestComponent";

class App extends Component {
  state = {
    data: null,
  };

  constructor() {
    super();
    this.ws = new MMSocket("ws://localhost:8888/");
  }

  componentDidMount() {
    this.ws.getAll((data) => {
      this.setState({ data: this.rebindData(data) });
    });
  }

  rebindData(data) {
    let { playlists, albums, artists, tracks } = data;
    for (let track of tracks) {
      track.playlists = track.playlist_ids.map((id) =>
        playlists.find((playlist) => playlist.id === id)
      );
      track.album = albums.find((album) => album.id === track.album_id);
    }
    for (let album of albums) {
      album.artists = album.artist_ids.map((id) =>
        artists.find((artist) => artist.id === id)
      );
    }
    return { playlists, albums, artists, tracks };
  }

  onPlaylistAdded(data) {
    this.setState({
      data: this.rebindData(mergePlaylistData(data, this.state.data)),
    });
  }

  render() {
    return (
      <Container fluid className="App">
        <Navbar bg="light" expand="lg">
          <Container>
            <Navbar.Brand href="#home">MusicMap</Navbar.Brand>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
              <Nav className="me-auto">
                <Nav.Link href="#home">Home</Nav.Link>
              </Nav>
            </Navbar.Collapse>
          </Container>
        </Navbar>
        <Row>
          <DatabaseScreen data={this.state.data}></DatabaseScreen>
        </Row>
        <Row>
          <FormQueryPlaylist
            ws={this.ws}
            onPlaylistAdded={this.onPlaylistAdded.bind(this)}
          ></FormQueryPlaylist>
          <TestComponent ws={this.ws}></TestComponent>
        </Row>
      </Container>
    );
  }
}

function mergePlaylistData(d1, d2) {
  return {
    playlists: d1.playlists.concat(d2.playlists),
    albums: d1.albums.concat(d2.albums),
    artists: d1.artists.concat(d2.artists),
    tracks: d1.tracks.concat(d2.tracks),
  };
}

export default App;
