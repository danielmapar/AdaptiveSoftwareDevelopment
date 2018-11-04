import React, { Component } from 'react'
import { withApollo, Mutation } from 'react-apollo'
import gql from 'graphql-tag'

const COMMANDS_MUTATION = gql`
  mutation updateCommandsMutation($froms: [String]!, $tos: [String]!, $listenerCommand: String!) {
    updateCommands(froms: $froms, tos: $tos, listenerCommand: $listenerCommand) {
  		userId
  		from
  		to
  	}
  }
`

const USER_QUERY = gql`
  query {
    me {
      listenerCommand
    }
  }
`

const COMMANDS_QUERY = gql`
  query {
    commands {
      userId
      from
      to
    }
  }
`

class Command extends Component {
  state = {
    froms: [],
    tos: [],
    listenerCommand: "",
    loading: false,
    error: null
  }

  addCommand() {
    const {froms, tos} = this.state;
    froms.push('')
    tos.push('')
    this.setState({ froms, tos });
  }

  fetchCommands() {
    const { froms, tos } = this.state

    this.setState({loading: true});

    Promise.all([
      this.props.client.query({
        query: COMMANDS_QUERY
      }),
      this.props.client.query({
        query: USER_QUERY
      }),
    ]).then(data => {
      const dataCommands = data[0].data.commands;
      const dataUser = data[1].data.me;
      dataCommands.forEach(command => {
        froms.push(command.from);
        tos.push(command.to);
      });
      this.setState({
        loading: false,
        froms,
        tos,
        listenerCommand: dataUser.listenerCommand ? dataUser.listenerCommand : ""
      });
    }).catch(() => {
      this.setState({error: "Failed to load commands!"});
    })
  }

  componentWillMount() {
    this.fetchCommands();
  }

  render() {
    const { froms, tos, listenerCommand, loading, error } = this.state

    if (loading) return <div>Fetching</div>
    if (error) return <div>Error</div>

    return (<div>
            Call command: <input
              className="mb2"
              value={listenerCommand}
              onChange={e => this.setState({ listenerCommand: e.target.value })}
              type="text"
              placeholder="Call command"
            />
            <hr />
            {froms.map((from, i) => {
            const to = tos[i];

            return (<span key={i}><div className="flex flex-column mt3">
              Listener command: <input
                className="mb2"
                value={from}
                onChange={e => {
                  froms[i] = e.target.value
                  this.setState({ froms })
                }}
                type="text"
                placeholder="Listener command"
              />
              Philips Hue command: <input
                className="mb2"
                value={to}
                onChange={e => {
                  tos[i] = e.target.value
                  this.setState({ tos })
                }}
                type="text"
                placeholder="Philips Hue command"
              />
              <button onClick={e => {
                tos.splice(i, 1);
                froms.splice(i, 1);
                this.setState({ tos, froms })
              }}>Remove</button>
            </div>
            <hr/>
            </span>);
            })}

            <button onClick={this.addCommand.bind(this)}>Add command</button>

            <Mutation
              mutation={COMMANDS_MUTATION}
              variables={{ froms, tos, listenerCommand }}
              onCompleted={() => this.props.history.push('/commands')}
            >
              {mutation => <button onClick={() => {
                alert("Saved!");
                mutation();
              }}>Save</button>}
            </Mutation>
          </div>
      );
  }
}

export default withApollo(Command)
