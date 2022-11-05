/**
  *
  * main() will be run when you invoke this action
  *
  * @param Cloud Functions actions accept a single parameter, which must be a JSON object.
  *
  * @return The output of this action, which must be a JSON object.
  *
  */
 function main(params) {
  // console.log(params);
  return new Promise(function (resolve, reject) {
      const { CloudantV1 } = require('@ibm-cloud/cloudant');
      const { IamAuthenticator } = require('ibm-cloud-sdk-core');
      const authenticator = new IamAuthenticator({ apikey: 'ERFKpnpTmzK6SUvcCBMWgspwM3YoBK3InnJroz72Pag2' })
      const cloudant = CloudantV1.newInstance({
          authenticator: authenticator
      });
      cloudant.setServiceUrl('https://68cba383-c45c-4641-82f8-39fe8b15d7cb-bluemix.cloudantnosqldb.appdomain.cloud');
      if (params.state) {
          // return dealership with this state 
          cloudant.postFind({db:'dealerships',selector:{state:params.state}})
          .then((result)=>{
            // console.log(result.result.docs);
            let code = 200;
            if (result.result.docs.length == 0) {
                code = 404;
            }
            resolve({
                statusCode: code,
                headers: { 'Content-Type': 'application/json' },
                body: result.result.docs
            });
          }).catch((err)=>{
            reject(err);
          })
      } else if (params.id) {
        // return dealership with this state 
        cloudant.postFind({db:'dealerships',selector:{id:parseInt(params.id)}})
        .then((result)=>{
          // console.log(result.result.docs);
          let code = 200;
          if (result.result.docs.length == 0) {
              code = 404;
          }
          resolve({
              statusCode: code,
              headers: { 'Content-Type': 'application/json' },
              body: result.result.docs
          });
        }).catch((err)=>{
          reject(err);
        })
      } else {
          // return all documents 
          //cloudant.postAllDocs({ db: 'dealerships', includeDocs: true, limit: 10 })
          cloudant.postAllDocs({ db: 'dealerships', includeDocs: true })            
          .then((result)=>{
            // console.log(result.result.rows);
            let code = 200;
            if (result.result.rows.length == 0) {
                code = 404;
            }
            resolve({
                statusCode: code,
                headers: { 'Content-Type': 'application/json' },
                body: result.result.rows
            });
          }).catch((err)=>{
            reject(err);
          })
    }
  }
)}