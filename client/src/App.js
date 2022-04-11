import React, { Component } from "react";
import { Container } from "react-bootstrap";
import { BrowserRouter, Route, Routes, Link } from "react-router-dom";

import "./App.css";

import Navigation from "./components/Navigation";
import Home from "./components/pages/Home";
import About from "./components/pages/About";
import SpotifyBrowser from "./components/pages/SpotifyBrowser";

class App extends Component {
  render() {
    return (
      <Container fluid>
        <BrowserRouter>
          <Navigation></Navigation>
          <Routes>
            <Route path="/" element={<Home />}></Route>
            <Route path="/spotify" element={<SpotifyBrowser />}></Route>
            <Route path="/about" element={<About />}></Route>
          </Routes>
        </BrowserRouter>
      </Container>
    );
  }
}

export default App;
