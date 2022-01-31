import * as THREE from 'three';

import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GUI } from 'three/examples/jsm/libs/lil-gui.module.min.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import  * as BufferGeometryUtils from 'three/examples/jsm/utils/BufferGeometryUtils.js';
import { Creature } from '../src/Creature.mjs';
import { Coordinate } from '../src/Coordinate.mjs';
import { Vector3 } from 'three';
import { AxisHelper } from 'three';

//let camera, scene, renderer;

class App {

	init() {

		this.camera = new THREE.PerspectiveCamera( 70, window.innerWidth / window.innerHeight, 1, 1000 );
		// In threejs the Y axis is up, unlike in all CAD Tools where Z is up
		// in GLTF Y is also the default up axis
	/*	this.camera.up.set( 0, 0, 1 );
		THREE.Object3D.DefaultUp.x = 0;
		THREE.Object3D.DefaultUp.y = 0;
		THREE.Object3D.DefaultUp.z = 1;
		*/

		this.camera.position.x = 400;
		this.camera.position.y = 400;
		this.camera.position.z = 400;
		
		this.scene = new THREE.Scene();
		this.scene.background = new THREE.Color( 0xffffff );

		this.create_material();
		this.create_Box();
		this.create_Axes();

		this.renderer = new THREE.WebGLRenderer( { antialias: true } );
		this.renderer.setPixelRatio( window.devicePixelRatio );
		this.renderer.setSize( window.innerWidth, window.innerHeight );
		document.body.appendChild( this.renderer.domElement );

		window.addEventListener( 'resize', onWindowResize, false );

		this.controls = new OrbitControls( this.camera, this.renderer.domElement );

		this.create_Creature();
		this.create_GUI();
		animate();
	}

	create_material() {
		this.material = new THREE.MeshBasicMaterial( {
			color: 0xffffff,
			polygonOffset: true,
			polygonOffsetFactor: 0.5, // positive value pushes polygon further away
			polygonOffsetUnits: 1
		} );
	}

	create_Axes() {
		this.axesHelper = new THREE.AxesHelper(5);
		this.axesHelper.l
		this.scene.add(this.axesHelper);
	}

	create_Box() {
		this.main_object = new THREE.Object3D();
		// mesh
		const geometry = new THREE.BoxBufferGeometry(200, 200, 200);
		//const material = new MeshBasicMaterial();
		const mesh = new THREE.Mesh(geometry, this.material);
		this.main_object.add(mesh);
		this.create_edges(this.main_object, mesh.geometry);
		this.scene.add(this.main_object);
		this.fitCameraToObject(mesh);
	}

	create_Sphere() {
		this.main_object = new THREE.Object3D();
		// mesh
		const geometry = new THREE.SphereBufferGeometry(100);
		//const material = new MeshBasicMaterial();
		const mesh = new THREE.Mesh(geometry, this.material);

		this.main_object.add(mesh);
		this.create_edges(this.main_object, mesh.geometry);

		this.scene.add(this.main_object);
		this.fitCameraToObject(mesh);

	}

	create_edges(parentObject3D, geometry) {
		// add lines for the edges
		const geo = new THREE.EdgesGeometry(geometry,1); 
		// not Wireframe because that gives lots of extra lines ....
	//	const geo = new WireframeGeometry(geometry); // or WireframeGeometry( geometry )?
		const mat = new THREE.LineBasicMaterial({ color: 0x000000, linewidth: 2 });

		const wireframe = new THREE.LineSegments(geo, mat);
		parentObject3D.add(wireframe);
	}

	activate_model() {
		//this.main_object = this.load_model('https://fvbakel.github.io/web-xr-hello/assets/2x4x3.gltf');
		this.main_object = this.load_model('https://fvbakel.github.io/web-xr-hello/assets/' + this.guiState.modelName + '.gltf');
		this.scene.add(this.main_object);
	}

	load_model(url) {
		const loaded_model = new THREE.Object3D();
		
		const loader = new GLTFLoader();
		loader.load( url, ( gltf ) => {
			// TODO cleanup and add loading progress bar
			const tmpGeomArray = [];
			gltf.scene.traverse( (child) => {
				if (child.isMesh) {
					tmpGeomArray.push(child.geometry);
				}
			} );
		//	const material = new MeshBasicMaterial();
			const geometry = BufferGeometryUtils.mergeBufferGeometries(tmpGeomArray,false);
			const mesh = new THREE.Mesh(geometry, this.material);
			loaded_model.add(mesh);
			this.create_edges(loaded_model ,geometry);
		//	const axesHelper = new THREE.AxesHelper(3);
		//	loaded_model.add(axesHelper);
		//	loaded_model.position = new Vector3(0,0,0);

			this.fitCameraToObject(mesh);
		/*	for (const mesh of tmpMeshArray) {
				loaded_model.add(mesh);
    			this.assign_default_material(mesh);
				this.create_edges(loaded_model ,mesh);
			}
			*/
		} );
		
		return loaded_model;

	}

	assign_default_material(mesh) {
		mesh.material = this.material;
		console.log('Default material assigned');
	}

	fitCameraToObject(mesh) {
		const offset = 1.25;
	//	const boundingBox = new Box3();
	
		if ( mesh.geometry.boundingBox == null ) mesh.geometry.computeBoundingBox();
		if ( mesh.geometry.boundingSphere == null ) mesh.geometry.computeBoundingSphere();
	//	boundingBox.setFromObject( this.main_object );
		let boundingBox = mesh.geometry.boundingBox;

		const wcs_center = new THREE.Vector3(0,0,0);
		const center = boundingBox.getCenter(wcs_center);
		const size   = boundingBox.getSize(wcs_center);
	
		// get the max side of the bounding box (fits to width OR height as needed )
		const maxDim = Math.max( size.x, size.y, size.z );
	//	const fov 	 = this.camera.fov * ( Math.PI / 180 );
//		let cameraZ  = Math.abs( maxDim / 4 * Math.tan( fov * 2 ) );
	
	//	cameraZ *= offset; // zoom out a little so that objects don't fill the screen
	
	//	this.camera.position.z = cameraZ;
	
	//	const minZ = boundingBox.min.z;
	//	const cameraToFarEdge = ( minZ < 0 ) ? -minZ + cameraZ : cameraZ - minZ;
	
	//	this.camera.far = cameraToFarEdge * 3;
	//	this.camera.updateProjectionMatrix();
	//	this.camera.lookAt( center );
		this.camera.position.x = maxDim * offset;
		this.camera.position.y = maxDim * offset;
		this.camera.position.z = maxDim * offset;
	//	center.z = -center.z;
		if ( this.controls ) {
			// set camera to rotate around center of loaded object
		//	this.controls.target = center;
		this.controls.target = wcs_center;

			// prevent camera from zooming out far enough to create far plane cutoff
		//	this.controls.maxDistance = cameraToFarEdge * 2;
		//	this.controls.saveState();
			this.controls.update();
			console.log('Controls updated');
		} else {
			this.camera.lookAt( center );
			console.log('Camera updated');
	    }
	}

	create_GUI() {
		
		this.current_shape = { name: 'Box' };
		const shapes = [ 'Box', 'Sphere','Load model' ];
		
		this.gui = new GUI();
		this.guiState = {
			awcsEnabled : true,
			wcsScale : 1,
			zoomFit : function() {
				window.app.zoomFit();
			},
			modelName : '2x4x3'
		}

		const viewControls = this.gui.addFolder('View');
		viewControls.add(this.guiState,'awcsEnabled')
			.name('Show WCS')
			.onChange(() => {
				if (this.axesHelper) {
					this.axesHelper.visible = this.guiState.awcsEnabled;
				}
		} );
		viewControls.add(this.guiState,'wcsScale',1,100,1)
			.name('WCS Size')
			.onChange(()=>{
				this.updateWcsScale();
		});
		viewControls.add(this.guiState,'zoomFit');
		viewControls.open();

		const shape_folder = this.gui.addFolder('Shape'); 
		const shapeCtrl = shape_folder.add( this.current_shape, 'name' ).options( shapes );
		shapeCtrl.name('Name');
		shapeCtrl.onChange( () => {
			this.shapeChange();

		} );
		shape_folder.add(this.guiState, 'modelName')
			.name('Model Name')
			.onChange( () => {
			this.shapeChange();
			} );
		shape_folder.open();
	}

	updateWcsScale() {
		if (this.axesHelper) {
			this.axesHelper.scale.x = this.guiState.wcsScale;
			this.axesHelper.scale.y = this.guiState.wcsScale;
			this.axesHelper.scale.z = this.guiState.wcsScale;
		}
	}

	shapeChange() {
		this.main_object.removeFromParent();
		this.main_object.traverse( (child) => {
			if (child.isMesh) {
				child.geometry.dispose();
				//child.material.dispose();
			}
		} );
		if (this.current_shape.name === 'Box') {
			this.create_Box();
		} else if (this.current_shape.name === 'Sphere') {
			this.create_Sphere();
		} else if ( this.current_shape.name === 'Load model') {
			this.activate_model();
		}
		
	}

	zoomFit() {
		// for now, just zoom to the first mesh
		if (this.main_object) {
			let mesh = null;
			for (const child of this.main_object.children) {
				if (child.isMesh) {
					mesh = child;
					break;
				}
			}
			if (mesh) {
				this.fitCameraToObject(mesh);
			}
		}
	}

	create_Creature() {
		const coordinate = new Coordinate(0,0,0);
		this.creature = new Creature(coordinate);
	}

	move_cycle() {
		if (this.creature.coordinate.y<50) {
			this.creature.move_forward(1);
		}
		this.main_object.position.x = this.creature.coordinate.x;
		this.main_object.position.y = this.creature.coordinate.y;
		this.main_object.position.z = this.creature.coordinate.z;
	}

}

function onWindowResize() {

	window.app.camera.aspect = window.innerWidth / window.innerHeight;
	window.app.camera.updateProjectionMatrix();

	window.app.renderer.setSize( window.innerWidth, window.innerHeight );

}

function animate() {

	requestAnimationFrame( animate );
//	window.app.move_cycle();
	window.app.renderer.render( window.app.scene, window.app.camera );

}

export default App;
