import React, { Component } from 'react';
import { ListGroup } from 'react-bootstrap';

class TrackList extends Component {
  render() {
    let trackItems;
    if (this.props.data !== null) {
        let trackData = this.props.data.tracks;
        trackItems = trackData.map(track => (<TrackItem data={track}></TrackItem>));
    }
    else {
        trackItems = (<div>No data loaded.</div>);
    }
    return (
        <ListGroup>
            {trackItems}
        </ListGroup>
    );
  }
}

class TrackItem extends Component {
    render() {
        return (
            <ListGroup.Item key={this.props.data.id}>
                {this.props.data.name}
            </ListGroup.Item>
        );
    }
}

export default TrackList;