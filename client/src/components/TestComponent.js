import React, { Component } from "react";
import { Button, Col, Container, ProgressBar, Row } from "react-bootstrap";
import MMSocket from "../utils/websocket.ts";

class TestComponent extends Component {
  /** @type {MMSocket} */
  ws;

  constructor(props) {
    super();
    this.state = { progress: null, status: 0, info: undefined };
    this.ws = props.ws;

		this.handleSend = this.handleSend.bind(this);
		this.handleProgress = this.handleProgress.bind(this);
		this.handleError = this.handleError.bind(this);
		this.handleEnd = this.handleEnd.bind(this);
  }

  handleSend(ev) {
    this.ws.progressTest(
      this.handleEnd,
      this.handleProgress,
      this.handleError
    );
  }

  handleEnd(data) {
		this.setState({
			status: 1,
			info: data
		});
	}

	handleProgress(percent) {
		this.setState({progress: percent});
	}

	handleError(err) {
		this.setState({
			status: 2,
			info: err
		});
	}

	renderInfo(state) {
		switch (state.status) {
			case 0:
				return "Progress at: " + state.progress;
			case 1:
				return "Completed with: " + state.info;
			case 2:
				return "Failed with: " + state.info;
		}
	}

  render() {
    return (
      <Container>
        <Row>
          <Col>
            <ProgressBar now={this.state.progress}></ProgressBar>
          </Col>
        </Row>
        <Row>
          <Col>
						{this.renderInfo(this.state)}
					</Col>
          <Col>
            <Button onClick={this.handleSend}>Test Progress</Button>
          </Col>
        </Row>
      </Container>
    );
  }
}

export default TestComponent;
