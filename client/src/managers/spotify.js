import { Buffer } from "buffer";

/** @enum {number} */
const authOptType = {
	init: 0,
	refresh: 1,
	get: 2
};

const spotifyUrls = {
	search: "https://api.spotify.com/v1/search"
};

class SpotifyConnector {
  client_id;
  client_secret;

  access_token;
  refresh_token;
	expires_at;

  constructor(client_id, client_secret) {
    this.client_id = client_id;
    this.client_secret = client_secret;
  }

	/**
	 * Get fetch options object based on desired operation.
	 * @private
	 * @param {authOptType} type 
	 * @returns {object}
	 */
	getAuthOpts(type) {
		let params;
		if (type === authOptType.get) {
			return {
				method: "GET",
				headers: {
					Authorization: "Bearer " + this.access_token
				}
			};
		}
		else if (type === authOptType.refresh) {
			params = {
				grant_type: "refresh_token",
				refresh_token: this.refresh_token,
			};
		}
		else if (type === authOptType.init) {
			params = {
				grant_type: "client_credentials"
			};
		}
		return {
		method: "POST",
		headers: {
			Authorization:
				"Basic " +
				new Buffer.from(this.client_id + ":" + this.client_secret).toString(
					"base64"
				),
			"Content-Type": "application/x-www-form-urlencoded",
		},
		json: true,
		body: new URLSearchParams(params)
		};
	};

	/**
	 * Try to initiate connection to Spotify API.
	 * @private
	 * @returns {Promise<string|undefined>} Promise with either access token or nothing if fail
	 */
  async startConnection() {
    var authOptions = this.getAuthOpts(authOptType.init);

    await fetch("https://accounts.spotify.com/api/token", authOptions)
      .then((res) => res.json())
      .then((body) => {
        this.access_token = body.access_token;
        this.refresh_token = body.refresh_token;
				this.expires_at = Date.now() + body.expires_in * 1000;
				console.log("SpotifyConnector successfully connected to Spotify API.")
      })
      .catch((reason) => {
        this.access_token = undefined;
        this.refresh_token = undefined;
				console.log("SpotifyConnector failed to connect to Spotify API (", reason, ").");
			});

    return this.access_token;
  }

	/**
	 * Try to refresh connection to Spotify API.
	 * @private
	 * @returns {Promise<string|undefined>} Promise with either access token or nothing if fail
	 */
  async refreshConnection() {
    if (!this.access_token) return false;

    var authOptions = this.getAuthOpts(authOptType.refresh);

    await fetch("https://accounts.spotify.com/api/token", authOptions)
      .then((res) => res.json())
      .then((body) => {
        this.access_token = body.access_token;
				console.log("SpotifyConnector successfully refreshed its connection to Spotify API.");
      })
      .catch((reason) => {
        this.access_token = undefined;
        this.refresh_token = undefined;
				console.error("SpotifyConnector failed to refresh connection to Spotify API (", reason, ").")
      });

    return this.access_token;
  }

	/**
	 * Ensures connection to Spotify API using other methods.
	 * @returns {Promise<string|undefined>} Promise with either access token or nothing if fail
	 */
	async checkConnection() {
		if (!this.access_token)
			return this.startConnection();
		else if (this.refresh_token && this.expires_at + 5000 > Date.now())
			return this.refreshConnection();
		return this.access_token;
	}

	/**
	 * 
	 * @param {String} query query to search for
	 * @todo Complex queries, e.g., "track:fun+artist:drake"
	 * @param {String|String[]} type One of "playlist|track|album|artist" or array containing subset of those
	 * @returns {Promise<Response>} Fetch response containing results
	 */
	async search(query, type) {
		await this.checkConnection();

		let url = new URL(spotifyUrls.search);
		url.search = new URLSearchParams({
			q: query,
			type: type
		});

		let authOptions = this.getAuthOpts(authOptType.get);

		return fetch(url, authOptions);
	}
}

export default SpotifyConnector;
