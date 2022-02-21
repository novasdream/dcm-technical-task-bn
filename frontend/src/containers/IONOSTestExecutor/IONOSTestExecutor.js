import React, {Component} from 'react';

import Aux from '../../hoc/Auxiliary/AuxComponent';
import TestExecutionTable from './../../components/TestExecutionTable/TestExecutionTable';

import axios from './../../axios-api'
import TestItemDetails from "../../components/TestItemDetails/TestItemDetails";
import AddNewRequest from "../../components/AddNewRequest/AddNewRequest";
import AddNewTest from '../../components/AddNewTest/AddNewTest';


class IONOSTestExecutor extends Component {
  state = {
    assets: {test_envs: [], available_paths: []},
    error: false,
    items: [],
    detailsView: false,
    itemID: null,
    currentItem: {},
    requesterError: '',
    envError: '',
    testPathError: '',
    requester: '',
    env: '',
    testPath: [],
    newTestFileStatus: 'idle',
    newTestFile: '',
    newTestFileError: ''
  };

  interval = null

  constructor(props) {
    super(props)
    this.fileInput = React.createRef();
  }
  updateAssets() {
    axios.get('assets').then(response => {
      this.setState({assets: response.data})
    }).catch(error => {
      this.setState({error: true})
    })
  }
  componentDidMount () {
    this.updateAssets()

    this.interval = setInterval(this.refreshList, 1000);
    this.refreshList()
  }
  componentWillUnmount() {
    clearInterval(this.interval);
  }

  getDisplayPath = (path) => {
    let val = '';
    this.state.assets.available_paths.map(item => {
      if (path.some(i => i === item.id)) {
        val += item.path + ' '
      }
    })
    return val;
  }

  refreshList = () => {
    axios.get('test-run').then(response => {
      let data = response.data;
      this.setState({items: data.map(item => { return {displayPath: this.getDisplayPath(item.path), ...item}})})
    }).catch(error => {
      this.setState({error: true})
    })
    if (this.state.itemID !== null){
      this.viewItemDetails(this.state.itemID)
    }
  }

  uploadNewTestFile = () => {
    if (this.fileInput.current.files.length < 1) {
      return
    }
    let form = new FormData();
    console.log(this.fileInput.current.files[0])
    form.append('file', this.fileInput.current.files[0], this.fileInput.current.files[0].name);
    this.setState({newTestFileStatus: 'uploading'})
    axios.post('test-file', form, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
    })
    .then(() => {
      alert('File uploaded successfully')
      this.updateAssets()
    })
    .catch(error => {
      if (error?.response?.data?.file[0]) {
        alert(error?.response?.data?.file[0])
      } else {
        alert('Error uploading file')
      }
    })
    .finally(() => {
      this.setState({newTestFileStatus: 'idle'})
    })
  }

  submitTest = () => {
    axios.post('test-run', {requested_by: this.state.requester, env: this.state.env, path: this.state.testPath}).then(response => {
      this.setState({requester: '', env: '', testPath: ''})
        this.refreshList()
      }).catch(error => {
        this.setState({
          requesterError: error.data.requested_by,
          envError: error.data.env,
          testPathError: error.data.path,
        })
      })
  }

  viewItemDetails = (itemId) => {
      axios.get('test-run/' + itemId).then(response => {
        let data = response.data
        data.displayPath = this.getDisplayPath(response.data.path)
        this.setState({currentItem: data})
      }).catch(error => {
        this.setState({error: true})
      })
    this.setState({
      detailsView: true,
      itemID: itemId
    })
  };

  backToListItems = () => {
    this.setState({
      detailsView: false,
      itemID: null
    })
  };

  handleTestPathChanged = (e) => {
    let options = e.target.options;
    let value = [];
    for (let i = 0, l = options.length; i < l; i++) {
      if (options[i].selected) {
        value.push(options[i].value);
      }
    }
    this.setState({testPath: value});
  }

  render () {
    if (this.state.detailsView) {
      return (
          <TestItemDetails currentItem={this.state.currentItem} backClicked={this.backToListItems}></TestItemDetails>
      )
    }
    return (
        <Aux>
          <AddNewTest
            fileInput={this.fileInput}
            newTestFileError={this.state.newTestFileError}
            uploadTestFile={_ => this.uploadNewTestFile()}
            status={this.state.newTestFileStatus}
          />
          <AddNewRequest
              requester={this.state.requester}
              requesterError={this.state.requesterError}
              env={this.state.env}
              envError={this.state.envError}
              testPath={this.state.testPath}
              testPathError={this.state.testPathError}
              assets={this.state.assets}

              requesterChanged={e => this.setState({ requester: e.target.value?.toString() })}
              envChanged={e => this.setState({ env: e.target.value?.toString() })}
              testPathChanged={this.handleTestPathChanged}
              submitTest={this.submitTest}
          ></AddNewRequest>
          <TestExecutionTable items={this.state.items} viewItemDetails={this.viewItemDetails}></TestExecutionTable>
      </Aux>
    )
  }
}

export default IONOSTestExecutor;
