import React, { Component } from "react";
import { Table, ListGroup, Container, Dropdown, Row, Col } from "react-bootstrap";

class DatabaseScreen extends Component {
	constructor() {
		super();
		this.state = {type: 'playlists'}
		this.handleTypeChange = this.handleTypeChange.bind(this);
	}
	
	handleTypeChange(ev) {
		this.setState({type: ev.target.getAttribute('data-type')});
	}

	render() {
		if (this.props.data === null) {
			return (<div>App isn't connected to the server...</div>)
		}

		let {playlists, albums, artists, tracks} = this.props.data;

		if ([playlists, albums, artists, tracks].every(arr=>arr.length === 0)) {
			return (<div>The server is empty, try populating with new data.</div>)
		}

		let items;
		switch(this.state.type) {
			case 'playlists':
				items = playlists.map(toListItem);
				break;
			case 'albums':
				items = albums.map(toListItem);
				break;
			case 'artists':
				items = artists.map(toListItem);
				break;
		}

		return (
			<Container>
				<Row>
					<Col md={2}>
						<Dropdown>
							<Dropdown.Toggle>Playlists</Dropdown.Toggle>
							<Dropdown.Menu>
								<Dropdown.Item onClick={this.handleTypeChange} data-type={'playlists'}>Playlists</Dropdown.Item>
								<Dropdown.Item onClick={this.handleTypeChange} data-type={'albums'}>Albums</Dropdown.Item>
								<Dropdown.Item onClick={this.handleTypeChange} data-type={'artists'}>Artists</Dropdown.Item>
							</Dropdown.Menu>
						</Dropdown>
						<ListGroup>{items}</ListGroup>
					</Col>
					<Col md={10}>
						<DatabaseTable data={tracks}></DatabaseTable>
					</Col>
				</Row>
			</Container>
		);
	}
}

class DatabaseTable extends Component {
  render() {
		if (this.props.data === null) {
			return (<div>No data loaded.</div>);
		}
		console.log("DBTable ", this.props.data);
		let tableRows = this.props.data.map((track) => (
			<DatabaseRow key={track.id} data={track}></DatabaseRow>
		));

    return (
      <Table striped bordered hover>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Album</th>
          </tr>
        </thead>
        <tbody>{tableRows}</tbody>
      </Table>
    );
  }
}

class DatabaseRow extends Component {
  render() {
		let track = this.props.data;
		return (
			<tr>
				<td>{track.id}</td>
				<td>{track.name}</td>
				<td>{track.album_id}</td>
			</tr>
		);
	}
}

function toListItem(obj) {
	return (<ListGroup.Item key={obj.id}>{obj.name}</ListGroup.Item>);
}

export default DatabaseScreen;