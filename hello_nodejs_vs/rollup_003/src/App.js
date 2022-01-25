import {
	BoxBufferGeometry,
	Mesh,
	MeshBasicMaterial,
	PerspectiveCamera,
	Scene,
	Color,
	WebGLRenderer,
	EdgesGeometry,
	LineBasicMaterial,
	LineSegments,
	Object3D,
	SphereBufferGeometry,
	Box3
} from 'three';

import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GUI } from 'three/examples/jsm/libs/lil-gui.module.min.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

import { Creature } from '../src/Creature.mjs';
import { Coordinate } from '../src/Coordinate.mjs';

//let camera, scene, renderer;

class App {

	init() {

		this.camera = new PerspectiveCamera( 70, window.innerWidth / window.innerHeight, 1, 1000 );
		this.camera.position.z = 400;

		this.scene = new Scene();
		this.scene.background = new Color( 0xffffff );

		this.create_Box();

		this.renderer = new WebGLRenderer( { antialias: true } );
		this.renderer.setPixelRatio( window.devicePixelRatio );
		this.renderer.setSize( window.innerWidth, window.innerHeight );
		document.body.appendChild( this.renderer.domElement );

		window.addEventListener( 'resize', onWindowResize, false );

		this.controls = new OrbitControls( this.camera, this.renderer.domElement );

		this.create_Creature();
		this.create_GUI();
		animate();
	}

	create_Box() {
		this.main_object = new Object3D();
		// mesh
		const geometry = new BoxBufferGeometry(200, 200, 200);
		const material = new MeshBasicMaterial();
		const mesh = new Mesh(geometry, material);
		this.main_object.add(mesh);

		// add lines for the edges
		const geo = new EdgesGeometry(geometry); // or WireframeGeometry( geometry )
		const mat = new LineBasicMaterial({ color: 0x000000, linewidth: 2 });

		const wireframe = new LineSegments(geo, mat);
		this.main_object.add(wireframe);
		this.scene.add(this.main_object);
	}

	create_Sphere() {
		this.main_object = new Object3D();
		// mesh
		const geometry = new SphereBufferGeometry(100);
		const material = new MeshBasicMaterial();
		const mesh = new Mesh(geometry, material);

		this.main_object.add(mesh);
		this.create_edges(this.main_object, mesh);

		this.scene.add(this.main_object);
	}

	create_edges(parentObject3D, mesh) {
		// add lines for the edges
		const geo = new EdgesGeometry(mesh.geometry); // or WireframeGeometry( geometry )?
		const mat = new LineBasicMaterial({ color: 0x000000, linewidth: 2 });

		const wireframe = new LineSegments(geo, mat);
		parentObject3D.add(wireframe);
	}

	activate_model() {
		this.main_object = this.load_model('https://fvbakel.github.io/web-xr-hello/assets/2x4x3.gltf');
		for (const child of this.main_object.children) {
			if (child.isMesh) {
				this.create_edges(this.main_object ,child);
			}
		}
		
		this.scene.add(this.main_object);
	}

	load_model(url) {
		const loaded_model = new Object3D();
		const loader = new GLTFLoader();
		loader.load( url, ( gltf ) => {
			loaded_model.add(gltf.scene);
			/*gltf.scene.traverse( (child) => {
				if (child.isMesh) {
					loaded_model.add(child);
					if (child.material === undefined) {
						this.assign_default_material(child);
					} else {
						console.log('Using model defined material');
					}
				}
			} );
		/*	for (const child of gltf.scene.children) {
				if (child.isMesh) {
					loaded_model.add(child);
					if (child.material === undefined) {
						this.assign_default_material(child);
					} else {
						console.log('Using model defined material');
					}
				}
			}
			*/

		} );


		return loaded_model;
	}

	assign_default_material(mesh) {
		const material = new MeshBasicMaterial( {
			color: 0x00ff00,
			wireframe: false
		} );
		mesh.material = material;
		console.log('Default material assigned');
	}

	fitCameraToObject() {

		const offset = 1.25;
	//	const boundingBox = new Box3();
	
		// get bounding box of object - this will be used to setup controls and camera
		
	//	boundingBox.setFromObject( this.main_object );
		
		const center = this.main_object.getCenter();
		const size = this.main_object.getSize();
	
		// get the max side of the bounding box (fits to width OR height as needed )
		const maxDim = Math.max( size.x, size.y, size.z );
		const fov = camera.fov * ( Math.PI / 180 );
		let cameraZ = Math.abs( maxDim / 4 * Math.tan( fov * 2 ) );
	
		cameraZ *= offset; // zoom out a little so that objects don't fill the screen
	
		this.camera.position.z = cameraZ;
	
		const minZ = this.main_object.min.z; // boundingBox.min.z;
		const cameraToFarEdge = ( minZ < 0 ) ? -minZ + cameraZ : cameraZ - minZ;
	
		this.camera.far = cameraToFarEdge * 3;
		this.camera.updateProjectionMatrix();
	
		if ( this.controls ) {
			// set camera to rotate around center of loaded object
			this.controls.target = center;

			// prevent camera from zooming out far enough to create far plane cutoff
			this.controls.maxDistance = cameraToFarEdge * 2;
			this.controls.saveState();
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
		const shape_folder = this.gui.addFolder('shape'); 
		const shapeCtrl = shape_folder.add( this.current_shape, 'name' ).options( shapes );
		
		shapeCtrl.onChange( function () {

			window.app.shapeChange();

		} );
		shape_folder.open();
	}

	shapeChange() {
		this.main_object.removeFromParent();
		if (this.current_shape.name === 'Box') {
			this.create_Box();
		} else if (this.current_shape.name === 'Sphere') {
			this.create_Sphere();
		} else if ( this.current_shape.name === 'Load model') {
			this.activate_model();
		}
		//this.fitCameraToObject();
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
	window.app.move_cycle();
	window.app.renderer.render( window.app.scene, window.app.camera );

}

export default App;
