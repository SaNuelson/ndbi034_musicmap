import { React, Component } from "react";
import { Container, Nav, Navbar } from "react-bootstrap";
import { NavLink } from "react-router-dom";

class Navigation extends Component {
	constructor(props) {
		super();
	}

  render() {
    return (
      <Navbar bg="light" expand="lg">
        <Container>
          <Navbar.Brand href="#home">MusicMap</Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
							<LinkItem name="Home" path="/" />
							<LinkItem name="SpotifyBrowser" path="/spotify" />
							<LinkItem name="About" path="/about" />
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>
    );
  }
}

function LinkItem(props) {
	return (<Nav.Link as={NavLink} to={props.path}>{props.name}</Nav.Link>);
}

export default Navigation;
